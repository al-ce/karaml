from collections import namedtuple
from dataclasses import dataclass
from re import findall, search

from karaml.helpers import (
    get_multi_keys, validate_mod_aliases, validate_optional_mod_sets,
    validate_sticky_mod_value, validate_sticky_modifier, validate_var_value,
    validate_shnotify_dict, validate_mouse_pos_args,
    check_and_validate_str_as_dict
)
from karaml.exceptions import invalidKey, invalidSoftFunct
from karaml.key_codes import KEY_CODE_REF_LISTS, MODIFIERS, PSEUDO_FUNCS

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
        if multichar_pf := multichar_func(usr_key):
            return multichar_pf
        return [key_code_translator(usr_key, usr_key)]

    translations = []
    shell_cmd = ""
    for key in multi_keys:
        if multichar_pf := multichar_func(key):
            translations += multichar_pf
            continue

        translated = key_code_translator(key, usr_key)

        if translated.key_type == "shell_command":
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


def key_code_translator(usr_key: str, usr_map: str) -> KeyStruct:
    """
    Given a user mapping, return a KeyStruct with the key_type, key_code, and
    modifiers for the mapping.
    A KeyStruct represents a single event, like a key press, a psuedo function,
    i.e one of the wrappers karaml provieds for common commands like executing
    a shell command, opening an app, etc., or a layer change, which is
    equivalent to setting a variable in Karabiner-Elements.
    If the mapping does not match any of these, then it is an invalid key code
    and an exception is raised.

    usr_key and usr_map are the same unless usr_key is a simul key mapping,
    e.g. for 'j+k', usr_map is `j+k' and usr_key are 'j' or 'k' on separate
    calls usr_map is passed for configError printing purposes
    """

    if layer := translate_if_layer(usr_key):
        return layer

    if to_event := translate_if_pseudo_func(usr_key):
        return to_event

    if keystruct := translate_if_valid_keycode(usr_key, usr_map):
        return keystruct

    invalidKey("key code", usr_map, usr_key)


def multichar_func(usr_key: str) -> list:
    """
    If a user mapping matches the regex 'string\\((.*)\\)', e.g.
    string(hello), return a list of KeyStructs with each character in parens as
    its key_code, given that all chars are valid key_codes or aliases.
    """

    multichar = search("string\\((.*)\\)", usr_key)
    if not multichar:
        return
    return [
        translate_if_valid_keycode(char, usr_key)
        for char in multichar.group(1)
    ]


def translate_if_layer(string: str) -> namedtuple:
    """
    Return a KeyStruct with the key_type 'layer' and the layer name as the
    key_code if the string matches the regex '^/(\\w+)/$', e.g. '/layer1/'.
    Otherwise, return None.
    """
    layer = search("^/(\\w+)/$", string)
    if not layer:
        return
    return KeyStruct("layer", layer.group(1), None)


def translate_if_pseudo_func(usr_map: str) -> KeyStruct:
    """
    Return a KeyStruct with the key_type and key_code for a pseudo function
    if the user mapping matches the regex for a pseudo function, e.g.
    'shell(open .)' or 'app(Terminal)'. Otherwise, return None.
    """
    for event_alias in PSEUDO_FUNCS:
        query = search(f"^{event_alias}\\((.+)\\)$", usr_map)
        if not query:
            continue

        event, command = translate_pseudo_func(event_alias, query.group(1))
        return KeyStruct(event, command, None)


def translate_pseudo_func(event: str, cmd: str) -> tuple[str, str]:
    """
    Takes a pseudo function event and command and returns a tuple with the
    event and command strings that will be used to create a KeyStruct.
    e.g. 'shell(open .)' -> ('shell_command', 'open .') for the KeyStruct

    KeyStruct('shell_command', 'open .', None)
    """
    # We don't actually check if the command/argument for 'open()' or
    # 'shell()' are valid links, commands, etc.) & trust the user

    # TODO: add validation for select_input_source, mouse_key, soft_func,
    # etc. For now, it's the user's responsibility

    match event:
        # NOTE: need to update PSEUDO_FUNCS if adding new events here
        case "app":
            event, cmd = "shell_command", f"open -a '{cmd}'.app"
        case "input":
            event, cmd = "select_input_source", input_source(cmd)
        case "mouse":
            event, cmd = "mouse_key", mouse_key(cmd)
        case "mousePos":
            event, cmd = "software_function", \
                        {"set_mouse_cursor_position": mouse_pos(cmd)}
        case "notify":
            event, cmd = "set_notification_message", notification(cmd)
        case "notifyOff":
            event, cmd = "set_notification_message", notification_off(cmd)
        case "open":
            event, cmd = "shell_command", f"open {cmd}"
        case "shell":
            event = "shell_command"
        case "shnotify":
            event, cmd = "shell_command", shnotify(cmd)
        case "softFunc":
            event = "software_function"
        case "sticky":
            event, cmd = "sticky_modifier", sticky_mod(cmd)
        case "var":
            event, cmd = "set_variable", set_variable(cmd)
    return event, cmd


def input_source(regex_or_dict: str) -> dict:
    """
    Returns a dictionary for the select_input_source event.
    If the user mapping is a dictionary, tranform the string into a dictionary,
    return the dictionary and trust that the user passed a valid dictionary for
    this event.
    If the user mapping is a string, e.g. 'English', return a dictionary with
    the key 'language' and the value of the string, e.g.
    {'language': 'English'}. The former is appropriate for complex mappings,
    e.g. where a distinction between polytonic and monotonic Greek is needed,
    the latter for simple switching between languages.
    """

    if check_and_validate_str_as_dict(regex_or_dict):
        return eval(regex_or_dict)
    return {"language": regex_or_dict.strip()}


def mouse_key(mouse_key_funcs: str) -> dict:
    """
    Returns a dictionary for the mouse_key event.
    If the user mapping is a dictionary, tranform the string into a dictionary,
    return the dictionary and trust that the user passed a valid dictionary for
    this event.
    If the user mapping is a string, e.g. 'x, 200', return a dictionary with
    the key 'x' and the value of the string, e.g. {'x': 200}.
    """

    if check_and_validate_str_as_dict(mouse_key_funcs):
        return eval(mouse_key_funcs)

    key, value = mouse_key_funcs.split(",")
    return {key.strip(): float(value.strip())}


def mouse_pos(mouse_pos_args: str) -> dict:
    """
    Takes the arguments for the mousePos() pseudo function and returns a
    dictionary for the software_function event for set_mouse_cursor_position.

    The pseudo function is 'mousePos(x, y, screen)' where x and y are integers
    and screen is an optional integer. The function returns a dictionary with
    the keys 'x', 'y', and 'screen' if the screen is specified.

    Example:
    mouse_pos(200, 300, 1) --> {'x': 200, 'y': 300, 'screen': 1}
    """

    validate_mouse_pos_args(mouse_pos_args)
    formatted_args = [int(arg.strip()) for arg in mouse_pos_args.split(",")]
    x, y, *screen = formatted_args

    mouse_pos_dict = {"x": x, "y": y}
    if screen:
        mouse_pos_dict["screen"] = int(screen[0])
    return mouse_pos_dict


def notification(id_and_message: str) -> dict:
    # id, text = id_and_message.split(",")
    # return {"id": id.strip(), "text": text.strip()}
    default = {"id": "", "text": ""}
    params = list(map(str.strip, id_and_message.split(",")))

    if len(params) == 1 or params[1].lower() == "null":
        default["text"] = ""
        default["id"] = params[0]
    elif len(params) == 2:
        default["id"] = params[0]
        default["text"] = params[1]
    return default


def notification_off(id: str) -> dict:
    """Alternate syntax for turning off a notification. A user might prefer
    this to passing no msg arg or 'null' as the message arg to notify()."""
    return {"id": id.strip(), "text": ""}


def shnotify_dict(n_dict: dict) -> str:
    validate_shnotify_dict(n_dict)
    if not n_dict.get("msg"):
        n_dict["msg"] = ""
    cmd = f"osascript -e 'display notification \"{n_dict['msg']}\""

    if n_dict.get("title"):
        cmd += f" with title \"{n_dict['title']}\""
    if n_dict.get("subtitle"):
        cmd += f" subtitle \"{n_dict['subtitle']}\""
    if n_dict.get("sound"):
        cmd += f" sound name \"{n_dict['sound']}\""

    return cmd + "'"  # close the osascript command


def shnotify(notification: str) -> str:

    if check_and_validate_str_as_dict(notification):
        return shnotify_dict(eval(notification))

    default = {
        "msg": "",
        "title": "",
        "subtitle": "",
        "sound": "",
    }

    params = list(map(str.strip, notification.split(",")))

    for i, key in enumerate(default.keys()):
        if i < len(params) and params[i].lower() != "null":
            default[key] = params[i]

    cmd = f"osascript -e 'display notification \"{default['msg']}\""

    if default["title"]:
        cmd += f" with title \"{default['title']}\""

    if default["subtitle"]:
        cmd += f" subtitle \"{default['subtitle']}\""

    if default["sound"]:
        cmd += f" sound name \"{default['sound']}\""

    return cmd + "'"  # close the osascript command


def soft_func(softfunc_args: str) -> dict:
    # TODO: This is easy to break, consider implementing
    # check_and_validate_str_as_dict() for this

    # Only accept well formed dict here
    sf_dict = eval(softfunc_args)
    if type(sf_dict) != dict:
        invalidSoftFunct(softfunc_args)
    return sf_dict


def sticky_mod(sticky_mod_values: str) -> dict:
    modifier, value = sticky_mod_values.split(",")
    validate_sticky_modifier(modifier.strip())
    validate_sticky_mod_value(value.strip())
    return {modifier.strip(): value.strip()}


def set_variable(condition_items: str) -> dict:
    # NOTE: We accept any int, but the layer system checks for 0 or 1.
    # So, we should either set a constraint here (check for 0 or 1) or
    # allow more values in the layer system, e.g. default to 1 for /nav/
    # but maybe check for value == 2 for /nav/2 ?

    name, value = map(str.strip, condition_items.split(","))
    validate_var_value(name, value)
    var_dict = {"name": name, "value": int(value)}
    return var_dict


def translate_if_valid_keycode(usr_key: str, usr_map: str) -> KeyStruct:
    for ref_list in KEY_CODE_REF_LISTS:
        key_code_type, ref = ref_list.key_type, ref_list.ref
        primary_key, modifiers = parse_primary_key_and_mods(usr_key, usr_map)

        if primary_key not in ref:
            continue

        if alias := resolve_alias(primary_key, key_code_type, ref, modifiers):
            return alias

        return KeyStruct(key_code_type, primary_key, modifiers)


def parse_primary_key_and_mods(usr_key: str, usr_map) -> tuple[str, dict]:
    if modded_key := is_modded_key(usr_key):
        modifiers: dict = get_modifiers(modded_key.modifiers, usr_map)
        return modded_key.key, modifiers
    return usr_key, {}


def is_modded_key(string: str) -> ModifiedKey:
    expr = "<(.+)-(.+)>"

    if query := search(expr, string):
        return ModifiedKey(*query.groups())


def get_modifiers(usr_mods: str, usr_map: str) -> dict:
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
    not_in_parens: list = findall(r"[\w+⌘⌥⌃⇧]+(?![^()]*\))", string)

    in_parens = list(in_parens[0]) if in_parens else None
    not_in_parens = list(not_in_parens[0]) if not_in_parens else None
    return not_in_parens, in_parens


def modifier_lookup(usr_mods: list) -> list:
    return [MODIFIERS.get(mod) for mod in usr_mods if MODIFIERS.get(mod)]


def resolve_alias(
        usr_key: str,
        key_code_type: str,
        alias_reference: dict,
        usr_mods: dict
) -> KeyStruct:

    if key_code_type != "alias":
        return
    alias = alias_reference[usr_key]
    alias_key, alias_mods = alias.key_code, alias.modifiers
    updated_usr_mods_dict = update_alias_modifiers(usr_mods, alias_mods)
    return KeyStruct("key_code", alias_key, updated_usr_mods_dict)


def update_alias_modifiers(modifiers_dict: dict, alias_mods: list) -> dict:
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
