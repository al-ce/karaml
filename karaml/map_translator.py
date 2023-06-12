from collections import namedtuple
from dataclasses import dataclass
from re import findall, search

from karaml.helpers import (
    get_multi_keys, validate_mod_aliases, validate_optional_mod_sets,
    check_and_validate_str_as_dict, is_layer,
)
from karaml.exceptions import invalidKey, invalidSoftFunct
from karaml.key_codes import (
    KEY_CODE_REF_LISTS,
    MODIFIERS,
    MODIFIER_ALIASES,
    ALIASES,
)
from karaml.templates import (
    TEMPLATES,
    translate_template,
)

KeyStruct = namedtuple("KeyStruct", ["key_type", "key_code", "modifiers"])
ModifiedKey = namedtuple("ModifiedKey", ["modifiers", "key"])


def queue_translations(usr_key: str) -> list:
    """
    Given a user mapping, return a list of KeyStructs for each key in the
    mapping that holds the key_type, key_code, and modifiers for each key.
    If the user mapping is a multi-key mapping, e.g. 'j+k', then return a list
    of KeyStructs for each key in the mapping. If the user mapping is a
    multi-character mapping, e.g. 'string(hello)', then return a list of
    KeyStructs for each character in the mapping.

    If the user mapping contains at least one shell based event, e.g.
    shell(open .) + app(Terminal), then combine all shell based events into one
    KeyStruct instead of appending each one to the list. This is because as of
    KE 13.7.0, multiple to.shell_command events are not supported to prevent
    slow shell commands from blocking the event queue, but we want to let the
    user separate them if they want to.
    """
    multi_keys = get_multi_keys(usr_key)
    if not multi_keys:
        usr_string_template = string_template(usr_key)
        return usr_string_template or [key_code_translator(usr_key, usr_key)]

    translations = []
    shell_cmd = ""
    for key in multi_keys:
        if string_pf := string_template(key):
            translations += string_pf
            continue
        translated = key_code_translator(key, usr_key)
        if translated and translated.key_type == "shell_command":
            shell_cmd = combine_shell_commands(translated, shell_cmd)
            continue
        translations.append(translated)

    if shell_cmd:
        translations.append(KeyStruct("shell_command", shell_cmd, None))
    return translations


def combine_shell_commands(keystruct: KeyStruct, shell_cmd: str) -> str:
    """
    Takes a KeyStruct with a shell based event and a combined shell command
    string and returns the updated combined shell command string, using '&&'
    to separate each shell command.

    These KeyStruct objects are no longer needed after this function is
    called, so they are not appended to the translations list. Instead, a new
    KeyStruct is created with the combined shell command string and appended
    to the translations list.
    """
    if not shell_cmd:
        return keystruct.key_code
    return shell_cmd + f" && {keystruct.key_code}"


def key_code_translator(usr_key: str, usr_map: str) -> KeyStruct | None:
    """
    Given a user mapping, return a KeyStruct with the key_type, key_code, and
    modifiers for the mapping.
    A KeyStruct represents a single event, like a key press, a template,
    (i.e one of the wrappers karaml provides for common commands like executing
    a shell command, opening an app, etc.), or a layer change, which is
    equivalent to setting a variable in Karabiner-Elements.
    If the mapping does not match any of these, then it is an invalid key code
    and an exception is raised.

    usr_key and usr_map are the same unless usr_key is a simul key mapping,
    e.g. for 'j+k', usr_map is `j+k' and usr_key are 'j' or 'k' on separate
    calls usr_map is passed for configError printing purposes
    """
    if layer := translate_if_layer(usr_key):
        return layer
    if to_event := translate_if_template(usr_key):
        return to_event
    if keystruct := translate_if_valid_keycode(usr_key, usr_map):
        return keystruct
    invalidKey("key code", usr_map, usr_key)


def string_template(usr_key: str) -> list:
    """
    If a user mapping matches the regex 'string\\((.*)\\)', e.g.
    string(hello), return a list of KeyStructs with each character in parens as
    its key_code, given that all chars are valid key_codes or aliases.

    If the string arg contains a modifier alias, e.g. string(⌘), or any other
    Unicode character that doesn't have a valid Karabiner-Elements keycode or
    karaml alias, then return a list with a single KeyStruct with the key_type
    'shell_command' and the shell command to send the Unicode string as its
    key_code. The shell command is an AppleScript that sets the clipboard to
    the string and then sends the paste command to the frontmost app. The prior
    contents of the clipboard are restored after the paste command is sent.
    """

    usr_string_template = search("string\\((.*)\\)", usr_key)
    if not usr_string_template:
        return []
    string_args = usr_string_template.group(1)

    key_codes = []
    for char in string_args:
        if char in MODIFIER_ALIASES:
            continue
        valid_key_code = translate_if_valid_keycode(char, usr_key)
        if valid_key_code:
            key_codes.append(valid_key_code)

    if len(string_args) > len(key_codes):
        return [send_Unicode_string(string_args)]
    return key_codes


def send_Unicode_string(string: str) -> KeyStruct:
    """
    Return a KeyStruct with the key_type 'shell_command' and the shell command
    to send the Unicode string as its key_code.
    """
    shell_cmd = (
        "osascript -e 'set temp to the clipboard as string' "
        f"-e 'set the clipboard to \"{string}\"' "
        "-e 'tell application \"System Events\" to keystroke \"v\" "
        "using command down' "
        "-e 'delay 0.1' -e 'set the clipboard to temp'"
    )

    return KeyStruct("shell_command", shell_cmd, None)


def translate_if_layer(string: str) -> namedtuple:
    """
    Return a KeyStruct with the key_type 'layer' and the layer name as the
    key_code if the string matches the regex determined in the is_layer func.
    Otherwise, return None.
    """
    layer = is_layer(string)
    if not layer:
        return
    return KeyStruct("layer", layer.group(1), None)


def translate_if_template(usr_map: str) -> KeyStruct:
    """
    Return a KeyStruct with the key_type and key_code for a template
    if the user mapping matches the regex for a template, e.g.
    'shell(open .)' or 'app(Terminal)'. Otherwise, return None.
    """
    # Check if the user mapping is an alias for a template, and if so,
    # replace the alias with the template
    if usr_map in ALIASES:
        usr_map = ALIASES[usr_map].key_code
    for template in TEMPLATES:
        query = search(f"^{template}\\((.+)\\)$", usr_map)
        if not query:
            continue
        event, command = translate_template(template, query.group(1))
        return KeyStruct(event, command, None)


def soft_func(softfunc_args: str) -> dict:
    """
    Return a dict with the soft function name as the key and the soft function
    args as the value if the soft function args are valid. Otherwise, raise an
    exception.
    """
    sf_dict = check_and_validate_str_as_dict(softfunc_args)
    if not sf_dict:
        invalidSoftFunct(softfunc_args)
    return sf_dict


def translate_if_valid_keycode(usr_key: str, usr_map: str) -> KeyStruct | None:
    """
    Return a KeyStruct with the key_type, key_code, and modifiers for the
    mapping if the user mapping uses valid Karaibner-Elements key_codes or
    karaml aliases. Otherwise, return None.
    """
    for ref_list in KEY_CODE_REF_LISTS:
        key_code_type, ref = ref_list.key_type, ref_list.ref
        primary_key, modifiers = parse_primary_key_and_mods(usr_key, usr_map)

        if primary_key not in ref:
            continue

        if alias := resolve_alias(primary_key, key_code_type, ref, modifiers):
            return alias

        return KeyStruct(key_code_type, primary_key, modifiers)


def parse_primary_key_and_mods(usr_key: str, usr_map) -> tuple[str, dict]:
    """
    Return the primary key and modifiers for the user mapping as a tuple.
    The primary key is a string representing a Karabiner-Elements key_code.
    The modifiers are a dict with the keys 'mandatory' and 'optional', each
    containing a list of Karabiner-Elements key_codes for the modifiers.
    """
    modded_key = is_modded_key(usr_key)
    if not modded_key:
        return usr_key, {}
    # The modifiers should either be ascii or unicode, but not a mix
    if bool(set(MODIFIER_ALIASES.keys()) & set(modded_key.modifiers)):
        modifiers_string: str = translate_unicode_mods(modded_key.modifiers)
    else:
        modifiers_string: str = modded_key.modifiers
    modifiers: dict = get_modifiers(modifiers_string, usr_map)
    return modded_key.key, modifiers


def translate_unicode_mods(modifiers: str) -> str:
    """
    Translate unicode modifiers to their corresponding ascii modifier aliases
    and return the translated string.

    Unlike the ascii modifiers, whose side is determined by whether they are
    lower or upper case, unicode modifiers' side are determined by whether they
    are prefixed or suffixed by a unicode 'arrow' character. This function
    handles the three cases: prefix, suffix, and neither.
    """
    translated_mods = ""
    for i, char in enumerate(modifiers):
        if char in ("(", ")"):
            translated_char = char
        elif char in ["‹", "›", " "]:
            continue
        elif i > 0 and modifiers[i-1] == "‹":
            translated_char = MODIFIER_ALIASES["‹" + char]
        elif i < len(modifiers) - 1 and modifiers[i + 1] == "›":
            translated_char = MODIFIER_ALIASES[char + "›"]
        else:
            translated_char = MODIFIER_ALIASES[char]
        translated_mods += translated_char

    return translated_mods


def is_modded_key(mapping: str) -> ModifiedKey | None:
    """
    Check if a mapping matches a valid syntax for a modified key. If so,
    return a ModifiedKey object with the key and modifiers. Otherwise,
    return None.

    A valid syntax must have a delimiter betwwen modifiers and the key (either
    a hyphen or a pipe). The modifiers may be enclosed in angle brackets.
    """

    mapping = mapping.strip()
    delim_expression = r"<?([^|>-]+)[|-]([^>]+)>?"
    delim_query = search(delim_expression, mapping)
    final_str_expression = r"(.*)\s+([^\s]+)$"
    final_str_query = search(final_str_expression, mapping)
    query = delim_query or final_str_query
    if not query:
        return
    modifiers, key = query.groups()
    modifiers = modifiers.replace(" ", "")
    key = key.strip()
    return ModifiedKey(modifiers, key)


def get_modifiers(usr_mods: str, usr_map: str) -> dict:
    """
    Return a dict with the keys 'mandatory' and 'optional', each containing
    a list of Karabiner-Elements key_codes for the modifiers, if the user
    modifiers are valid. Otherwise, raise an exception.
    """
    validate_mod_aliases(usr_mods)
    mods = {}
    mandatory, optional = parse_chars_in_parens(usr_mods)
    if mandatory:
        mods["mandatory"] = modifier_lookup(mandatory)
    if optional:
        mods["optional"] = modifier_lookup(optional)

    if not mods:
        invalidKey("modifier", usr_map, usr_mods)
    return mods


def parse_chars_in_parens(string: str) -> tuple:
    """
    Parse a string to check for characters in parens and not in parens.
    Returns a tuple of two lists, the first containing characters not in
    parens, representing mandatory modifiers, and the second containing
    characters in parens, representing optional modifiers.
    """
    in_parens: list = findall(r"\((.*?)\)", string)
    validate_optional_mod_sets(string, in_parens)
    not_in_parens: list = findall(r"[\w+]+(?![^()]*\))", string)

    in_parens = list(in_parens[0]) if in_parens else None
    not_in_parens = list(not_in_parens[0]) if not_in_parens else None
    return not_in_parens, in_parens


def modifier_lookup(usr_mods: list) -> list:
    """
    Return a list of Karabiner-Elements key_codes corresponding to the
    user's modifier aliases. e.g. a list of `['c, 's']` would return
    `['left_control', 'left_shift'].`
    """
    return [MODIFIERS.get(mod) for mod in usr_mods if MODIFIERS.get(mod)]


def resolve_alias(
        usr_key: str,
        key_code_type: str,
        alias_reference: dict,
        usr_mods: dict
) -> KeyStruct | None:
    """
    If the user key is an alias, return a KeyStruct with the key_code and
    modifiers for the alias. Otherwise, return None.
    """

    if key_code_type != "alias":
        return
    alias = alias_reference[usr_key]
    alias_key, alias_mods = alias.key_code, alias.modifiers
    updated_usr_mods_dict = update_alias_modifiers(usr_mods, alias_mods)
    return KeyStruct("key_code", alias_key, updated_usr_mods_dict)


def update_alias_modifiers(modifiers_dict: dict, alias_mods: list) -> dict:
    """
    Update a modifiers dict of an key_code alias's KeyStruct with any modifiers
    required by the alias. If no modifiers are required, return the original
    modifiers dict. Otherwise, return a new dict with the user's modifiers
    added to the original dict.

    For example, the alias `(` is defined by the following Alias object:

    `"(": Alias("9", alias_shift_mod)`

    Where `alias_shift_mod` == `["shift]`. So, the KeyStruct needs to be
    updated to include a shift modifier in its `modifiers` attribute.
    """
    if not alias_mods:
        return modifiers_dict
    elif not modifiers_dict:
        return {'mandatory': alias_mods}

    if not modifiers_dict.get('mandatory'):
        modifiers_dict['mandatory'] = alias_mods
    else:
        modifiers_dict['mandatory'] += alias_mods
    return modifiers_dict


@ dataclass
class TranslatedMap:
    """Translates a user-defined keymap into a list of namedtuples with the
    attributes `key_type`, `key_code`, and `modifiers`."""

    map: str

    def __post_init__(self):
        translated_keys = queue_translations(self.map)
        self.keys: list[KeyStruct] = translated_keys
