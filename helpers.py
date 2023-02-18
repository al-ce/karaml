import ast
from copy import copy
from collections import namedtuple
from itertools import chain
from re import search

from key_codes import MODIFIERS, TO_EVENTS

KeyStruct = namedtuple("KeyStruct", ["key_type", "key_code", "modifiers"])


def all_in(items: list, container: iter) -> bool:
    for item in items:
        if item not in container:
            return False
    return True


def condition_dict(layer_name: str, value: int) -> dict:
    return {"name": layer_name, "type": "variable_if", "value": value}


def dict_eval(string: str):

    try:
        ast_dict = ast.literal_eval(string)
        return eval(string) if isinstance(ast_dict, dict) else None

    except (ValueError, SyntaxError):
        return False


def filter_list(unfiltered):
    return list(chain.from_iterable([x for x in unfiltered if x]))


def get_multi_keys(string: str):
    if "+" in string:
        return string.split("+")


def invalidKey(key_type: str, map: str, key: str):
    key_type = "modifier" if key_type == "mod" else "key code"
    return f"Invalid user-defined {key_type} in map {map}: {key}"


def invalidToModType(usr_to_map: str):
    raise Exception(f"Opt flag for 'to.modifiers' not allowed: {usr_to_map}")


def is_dict(obj):
    return isinstance(obj, dict)


def is_layer(string: str):
    layer = search("^/(\\w+)/$", string)
    if not layer:
        return
    return KeyStruct("layer", layer.group(1), None)


def is_modded_key(string: str):
    expr = "<(.+)-(.+)>"

    if query := search(expr, string):
        ModifiedKey = namedtuple("ModifiedKey", ["modifiers", "key"])
        return ModifiedKey(*query.groups())


def make_list(x) -> list:
    return [x] if not isinstance(x, list) else x


def modifier_lookup(usr_mods: list) -> list:
    return [MODIFIERS.get(mod) for mod in usr_mods if MODIFIERS.get(mod)]


def parse_chars_in_parens(string: str):
    in_parens = search(r"\((.*?)\)", string)
    not_in_parens = search(r"[\w+]+(?![^()]*\))", string)
    in_parens = [in_parens[0]] if in_parens else None
    not_in_parens = [not_in_parens[0]] if not_in_parens else None
    return not_in_parens, in_parens


def requires_sublayer(layer_name: str) -> str:
    conditions = {"conditions": []}
    found_layer = search("^/(\\w+)/$", layer_name)
    if not found_layer or found_layer.group(1) == "base":
        return conditions
    layer_condition = condition_dict(f"{found_layer.group(1)}_sublayer", 1)
    conditions["conditions"].append(layer_condition)
    return conditions


def toggle_layer_off(karamlized_key):
    layer_off = copy(karamlized_key)
    layer_off.conditions["conditions"][0]["value"] = 1
    layer_off._to["to_if_alone"][0]["value"] = 0
    return layer_off


def to_event_check(usr_map: str):
    for event_alias in TO_EVENTS:
        query = search(f"{event_alias}\\((.*)\\)", usr_map)
        if not query:
            continue

        event, command = translate_event(event_alias, query.group(1))
        return KeyStruct(event, command, None)


def translate_event(event: str, command: str):

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
