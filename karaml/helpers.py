import ast
from re import search

from karaml.exceptions import (
    invalidFlag, invalidStickyModifier, invalidLayerName, invalidModifier,
    invalidOpt, invalidParamKeys, invalidParamValues, invalidStickyModValue
)
from karaml.key_codes import MODIFIERS, STICKY_MODS


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


def get_multi_keys(string: str) -> list:
    if "+" in string:
        return [s.strip() for s in string.split("+")]


def is_layer(string: str):
    return search("^/(\\w+)/$", string)


def is_dict(obj):
    return isinstance(obj, dict)


def make_list(x) -> list:
    return [x] if not isinstance(x, list) else x


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


def validate_layer(string: str):
    return search("^/(\\w+)/$", string).group(1) or invalidLayerName(string)


def validate_mods(mods: str):
    mods = mods.replace("(", "").replace(")", "")
    for char in mods:
        if char not in MODIFIERS.keys():
            invalidModifier(char, mods)


def validate_opt(string: str) -> str:
    valid = ["lazy", "repeat"]
    if (opt := string[1:]) in valid:
        return opt
    invalidOpt(string)


def validate_sticky_mod_value(string: str):
    if string not in ["on", "off", "toggle"]:
        invalidStickyModValue(string)


def validate_sticky_modifier(string: str):
    if string not in STICKY_MODS:
        invalidStickyModifier(string)
    print("SUCCESS!")
