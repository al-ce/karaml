from collections import namedtuple
from dataclasses import dataclass
from re import findall, search

from exceptions import invalidKey
from key_codes import KEY_CODE_REF_LISTS, MODIFIERS, TO_EVENTS

KeyStruct = namedtuple("KeyStruct", ["key_type", "key_code", "modifiers"])


def get_modifiers(usr_mods: str, usr_map: str) -> dict:
    mods = {}
    mandatory, optional = parse_chars_in_parens(usr_mods)
    if mandatory:
        mods["mandatory"] = modifier_lookup(mandatory)
    if optional:
        mods["optional"] = modifier_lookup(optional)

    if not mods:
        raise Exception(invalidKey("modifier", usr_map, usr_mods))
    return mods


def get_multi_keys(string: str) -> list:
    if "+" in string:
        return string.split("+")


def is_layer(string: str) -> namedtuple:
    layer = search("^/(\\w+)/$", string)
    if not layer:
        return
    return KeyStruct("layer", layer.group(1), None)


def is_modded_key(string: str) -> namedtuple:
    expr = "<(.+)-(.+)>"

    if query := search(expr, string):
        ModifiedKey = namedtuple("ModifiedKey", ["modifiers", "key"])
        return ModifiedKey(*query.groups())


def is_valid_keycode(usr_key, usr_map) -> namedtuple:
    for ref_list in KEY_CODE_REF_LISTS:
        event, ref = ref_list.key_type, ref_list.ref
        parsed_key, modifiers = parse_modifiers(usr_key, usr_map)

        if parsed_key not in ref:
            continue

        if alias := resolve_alias(parsed_key, event, ref, modifiers):
            # alias_key, alias_mods = alias.key, alias.modifiers
            # alias_mods = update_alias_modifiers(modifiers, alias_mods)
            # return KeyStruct("key_code", alias_key, alias_mods)
            return alias

        return KeyStruct(event, parsed_key, modifiers)


def modifier_lookup(usr_mods: list) -> list:
    return [MODIFIERS.get(mod) for mod in usr_mods if MODIFIERS.get(mod)]


def parse_chars_in_parens(string: str) -> tuple:
    in_parens = findall(r"\((.*?)\)", string)
    not_in_parens = findall(r"[\w+]+(?![^()]*\))", string)
    in_parens = list(in_parens[0]) if in_parens else None
    not_in_parens = list(not_in_parens[0]) if not_in_parens else None
    return not_in_parens, in_parens


def parse_modifiers(usr_key: str, usr_map) -> tuple:
    if modded_key := is_modded_key(usr_key):
        modifiers = get_modifiers(modded_key.modifiers, usr_map)
        return modded_key.key, modifiers
    return usr_key, None


def resolve_alias(usr_key: str, event: str, aliases_dict, mod_dict):
    if event != "alias":
        return
    alias = aliases_dict[usr_key]
    alias_key, alias_mods = alias.key_code, alias.modifiers
    alias_mods = update_alias_modifiers(mod_dict, alias_mods)
    return KeyStruct("key_code", alias_key, alias_mods)


def update_alias_modifiers(modifiers_dict: dict, alias_mods: list):
    if not alias_mods:
        return modifiers_dict
    return {'mandatory': alias_mods}


def to_event_check(usr_map: str) -> namedtuple:
    for event_alias in TO_EVENTS:
        query = search(f"{event_alias}\\((.*)\\)", usr_map)
        if not query:
            continue

        event, command = translate_event(event_alias, query.group(1))
        return KeyStruct(event, command, None)


def translate_event(event: str, command: str) -> tuple:

    match event:
        case "app":
            event, command = "shell_command", f"open -a '{command}'.app"
        case "shell":
            event = "shell_command"
        case "input":
            event = "select_input_source"
        case "mouse":
            event = "mouse_key"
        case "softFunc":
            event = "software_function"
    return event, command


@dataclass
class TranslatedMap:
    """Translates a user-defined keymap into a list of namedtuples with the
    attributes `key_type`, `key_code`, and `modifiers`."""

    map: str

    def __post_init__(self):
        translated_keys = self.queue_translations(self.map)
        self.keys: list = translated_keys

    def key_code_translator(self, parsed_key: str) -> namedtuple:

        if layer := is_layer(self.map):
            return layer

        if to_event := to_event_check(self.map):
            return to_event

        if keystruct := is_valid_keycode(parsed_key, self.map):
            return keystruct

        raise Exception(invalidKey("key code", self.map, parsed_key))

    def queue_translations(self, parsed_key: str) -> list:
        if multi_keys := get_multi_keys(parsed_key):
            return [self.key_code_translator(k.strip()) for k in multi_keys]
        else:
            return [self.key_code_translator(parsed_key)]
