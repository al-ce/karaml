import ast
from copy import copy
from exceptions import invalidFlag, invalidOpt


def dict_eval(string: str):
    try:
        ast_dict = ast.literal_eval(string)
        return eval(string) if isinstance(ast_dict, dict) else None
    except (ValueError, SyntaxError):
        return False


def flag_check(string: str):
    flags = {"+": True, "-": False}
    if (flag := string[0]) in flags:
        return flags[flag]
    invalidFlag(string)


def valid_opt(string: str) -> str:
    valid = ["lazy", "halt", "repeat"]
    if (opt := string[1:]) in valid:
        return opt
    invalidOpt(string)


def is_dict(obj):
    return isinstance(obj, dict)


def make_list(x) -> list:
    return [x] if not isinstance(x, list) else x


def toggle_layer_off(karamlized_key):
    layer_off = copy(karamlized_key)
    layer_off.conditions["conditions"][0]["value"] = 1
    layer_off._to["to_if_alone"][0]["value"] = 0
    return layer_off
