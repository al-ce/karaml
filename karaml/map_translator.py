from collections import namedtuple
from dataclasses import dataclass
from re import findall, search

from karaml.helpers import (
    get_multi_keys, validate_mod_aliases, validate_optional_mod_sets,
    validate_sticky_mod_value, validate_sticky_modifier, validate_var_value
)
from karaml.exceptions import invalidKey, invalidSoftFunct
from karaml.key_codes import KEY_CODE_REF_LISTS, MODIFIERS, TO_EVENTS

KeyStruct = namedtuple("KeyStruct", ["key_type", "key_code", "modifiers"])
ModifiedKey = namedtuple("ModifiedKey", ["modifiers", "key"])


def queue_translations(usr_key: str) -> list:
    multi_keys = get_multi_keys(usr_key)
    if not multi_keys:
        if multichar_pf := multichar_func(usr_key):
            return multichar_pf
        return [key_code_translator(usr_key, usr_key)]

    translations = []
    for k in multi_keys:
        if multichar_pf := multichar_func(k):
            translations += multichar_pf
            continue
        translations.append(key_code_translator(k, usr_key))
    return translations


def key_code_translator(usr_key: str, usr_map: str) -> KeyStruct:
    # usr_key and usr_map are the same unless it is a simul key mapping, e.g.
    # for 'j+k', usr_map is `j+k' and usr_key are 'j' or 'k' on separate calls
    # usr_map is passed for configError printing purposes

    if layer := is_layer(usr_key):
        return layer

    if to_event := special_to_event_check(usr_key):
        return to_event

    if keystruct := is_valid_keycode(usr_key, usr_map):
        return keystruct

    invalidKey("key code", usr_map, usr_key)


def multichar_func(usr_key: str):
    """If a user mapping matches the regex 'string\\((.*)\\)', e.g.
    string(hello), return a list of KeyStructs with each character in parens as
    its key_code, given that all chars are valid key_codes or aliases."""

    multichar = search("string\\((.*)\\)", usr_key)
    if not multichar:
        return
    return [is_valid_keycode(char, usr_key) for char in multichar.group(1)]


def is_layer(string: str) -> namedtuple:
    layer = search("^/(\\w+)/$", string)
    if not layer:
        return
    return KeyStruct("layer", layer.group(1), None)


def special_to_event_check(usr_map: str) -> namedtuple:
    for event_alias in TO_EVENTS:
        query = search(f"{event_alias}\\((.+)\\)", usr_map)
        if not query:
            continue

        event, command = translate_event(event_alias, query.group(1))
        return KeyStruct(event, command, None)


def translate_event(event: str, command: str) -> tuple:

    # We don't actually validate the command/argument for 'open()' or
    # 'shell()'_is (e.g. is it a valid link or command, etc.) & trust the user

    # TODO: add validation for select_input_source, mouse_key, soft_func,
    # etc. For now, it's the user's responsibility

    match event:
        case "app":
            event, command = "shell_command", f"open -a '{command}'.app"
        case "input":
            event, command = "select_input_source", input_source(command)
        case "mouse":
            event, command = "mouse_key", mouse_key(command)
        case "notify":
            event, command = "set_notification_message", notification(command)
        case "open":
            event, command = "shell_command", f"open {command}"
        case "shell":
            event = "shell_command"
        case "softFunc":
            event = "software_function"
        case "sticky":
            event, command = "sticky_modifier", sticky_mod(command)
        case "var":
            event, command = "set_variable", set_variable(command)
    return event, command


def input_source(regex_or_dict: str) -> dict:
    if regex_or_dict.startswith("{") and regex_or_dict.endswith("}") and \
            type(eval(regex_or_dict)) == dict:
        return eval(regex_or_dict)

    return {"language": regex_or_dict.strip()}


def mouse_key(mouse_key_funcs: str) -> dict:
    if mouse_key_funcs.startswith("{") and mouse_key_funcs.endswith("}") and \
            type(eval(mouse_key_funcs)) == dict:
        return eval(mouse_key_funcs)

    key, value = mouse_key_funcs.split(",")
    return {key.strip(): float(value.strip())}


def notification(id_and_message: str) -> dict:
    id, text = id_and_message.split(",")
    return {"id": id.strip(), "text": text.strip()}


def soft_func(softfunc_args: str) -> dict:
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


def is_valid_keycode(usr_key: str, usr_map: str) -> KeyStruct:
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
    in_parens: list = findall(r"\((.*?)\)", string)
    validate_optional_mod_sets(string, in_parens)
    not_in_parens: list = findall(r"[\w+]+(?![^()]*\))", string)
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


def update_alias_modifiers(modifiers_dict: dict, alias_mods: list):
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
