import ast
from copy import copy
from exceptions import (
    invalidFlag, invalidOpt, invalidParamKeys, invalidParamValues
)


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


def translate_params(params: dict) -> dict:
    param_aliases = {
        "a": "basic.to_if_alone_timeout_milliseconds",
        "h": "basic.to_if_held_down_threshold_milliseconds",
        "d": "basic.to_delayed_action_delay_milliseconds",
        "s": "basic.simultaneous_threshold_milliseconds",
        "m": "mouse_motion_to_scroll.speed",
    }
    default_param_names = [
        "basic.simultaneous_threshold_milliseconds",
        "basic.to_delayed_action_delay_milliseconds",
        "basic.to_if_alone_timeout_milliseconds",
        "basic.to_if_held_down_threshold_milliseconds",
        "mouse_motion_to_scroll.speed",
    ]
    translated = {}
    for k, v in params.items():
        if k in param_aliases:
            translated[param_aliases.get(k)] = v
        elif k in default_param_names:
            translated[k] = v
        else:
            invalidParamKeys(params, k)
        if type(v) != int:
            invalidParamValues(params, v)
    return {"parameters": translated} if translated else None
