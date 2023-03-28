import ast
from re import search

from karaml.exceptions import (
    invalidConditionName, invalidConditionValue, invalidFlag,
    invalidStickyModifier, invalidLayerName, invalidModifier,
    invalidTotalParensInMods, invalidToOpt, invalidParamKeys,
    invalidParamValues, invalidStickyModValue, invalidSHNotifyDict,
)
from karaml.key_codes import MODIFIERS, STICKY_MODS


def dict_eval(string: str) -> dict:
    try:
        ast_dict = ast.literal_eval(string)
        return eval(string) if isinstance(ast_dict, dict) else None
    except (ValueError, SyntaxError):
        return ""


def flag_check(string: str) -> bool:
    flags = {"+": True, "-": False}
    if (flag := string[0]) in flags:
        return flags[flag]
    invalidFlag(string)


def get_multi_keys(string: str) -> list:
    if "+" in string:
        return [s.strip() for s in string.split("+")]


def is_layer(string: str) -> bool:
    return search("^/(\\w+)/$", string)


def is_dict(obj) -> bool:
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
    return {"parameters": translated} if translated else {}


def validate_condition_dict(condition_dict: dict):
    name, cond_type, value = list(condition_dict.values())
    if not 0 <= value <= 1:
        invalidConditionValue(name, value)
    if not search("^[a-zA-Z_]+$", name):
        invalidConditionName(name)


def validate_shnotify_dict(notification_dict: dict):
    valid = ["msg", "title", "subtitle", "sound"]
    for k in notification_dict:
        if k not in valid:
            invalidSHNotifyDict(notification_dict, k)


def validate_layer(string: str) -> str:
    return search("^/(\\w+)/$", string).group(1) or invalidLayerName(string)


def validate_mod_aliases(mods: str) -> str:
    mods = mods.replace("(", "").replace(")", "")
    for char in mods:
        if char not in MODIFIERS.keys():
            invalidModifier(char, mods)
    return mods


def validate_to_opts(string: str) -> str:
    valid = ["lazy", "repeat"]
    if (opt := string[1:]) in valid:
        return opt
    invalidToOpt(string)


def validate_optional_mod_sets(mod_string: str, opt_mod_matches: list):
    if len(opt_mod_matches) > 1 or search("\\w+\\(\\w+\\)\\w+", mod_string):
        invalidTotalParensInMods(mod_string, opt_mod_matches)


def validate_sticky_mod_value(string: str):
    if string not in ["on", "off", "toggle"]:
        invalidStickyModValue(string)


def validate_sticky_modifier(string: str):
    if string not in STICKY_MODS:
        invalidStickyModifier(string)


def validate_var_value(name: str, value: str):
    try:
        value = int(value)
    except ValueError:
        invalidConditionValue(name, value)
    if not 0 <= int(value) <= 1:
        invalidConditionValue(name, value)
