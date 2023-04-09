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
    """
    Returns the value of the flag in the string for the to-event options
    'lazy' and 'repeat' after checking if the flag is valid.
    """
    flags = {"+": True, "-": False}
    if (flag := string[0]) in flags:
        return flags[flag]
    invalidFlag(string)


def get_multi_keys(string: str) -> list:
    """
    Returns a list of keys from a string of keys separated by a '+'.
    The '+' char is used to concatenate multiple keys in a 'from' or 'to'
    event, e.g.

    j+k: escape + notify(id1, Hello World)

    The above example will send the escape key when the j and k keys are
    pressed simultaneously, and will also send a notification with the
    message 'Hello World'. White space is ignored in the string.
    """
    if "+" in string:
        return [s.strip() for s in string.split("+")]


def is_layer(string: str) -> bool:
    """
    Returns True if the string matches the regex for an acceptable layer name.

    This function is used for a different purpose than the validate_layer_name
    function. It is used to determine what kind of to-event to assign the
    string to. If it is a layer, we might want to assign it to a 'to' event
    rather than a 'to_if_held_down' event so the layer can be accessed
    immediately without waiting for the 'to_if_held_down_threshold'.
    """
    return search("^/(\\w+)/$", string)


def is_dict(obj) -> bool:
    return isinstance(obj, dict)


def make_list(x) -> list:
    return [x] if not isinstance(x, list) else x


def translate_params(params: dict) -> dict:
    """
    Convert the aliased parameter keys to valid parameter names for the
    following parameters:

    a -> basic.to_if_alone_timeout_milliseconds
    h -> basic.to_if_held_down_threshold_milliseconds
    d -> basic.to_delayed_action_delay_milliseconds
    s -> basic.simultaneous_threshold_milliseconds
    m -> mouse_motion_to_scroll.speed

    The default parameter names are used if the parameter is not in the
    param_aliases dict. These parameters can be overridden by the user
    in the Karabiner-Elements GUI.
    """

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
    """
    Confirm that the user is only using valid keys in the shnotify() dict if
    they are using a dict rather than positional arguments.
    shnotify() is a wrapper for the shell command 'osascript -e' that
    sends a notification to the user via the macOS Notification Center using
    AppleScript. The dict keys are the same as some AppleScript arguments
    for the 'display notification' command.
    """
    valid = ["msg", "title", "subtitle", "sound"]
    for k in notification_dict:
        if k not in valid:
            invalidSHNotifyDict(notification_dict, k)


def validate_layer(string: str) -> str:
    """
    Returns the layer name if the string matches the regex for an acceptable
    layer name. Otherwise, it raises an error.

    The format must be a string enclosed in forward slashes, e.g. '/layer1/'
    with only alphanumeric characters and underscores.
    """
    return search("^/(\\w+)/$", string).group(1) or invalidLayerName(string)


def validate_mod_aliases(mods: str) -> str:
    """
    Check that all the modifier aliases in the string are valid.
    The return value is only used for testing. In the main program, this
    function is called for its side effect of raising an error if the
    string contains an invalid modifier alias. So the original modifier string
    is used in the main program after this function is called.
    """

    mods = mods.replace("(", "").replace(")", "")
    for char in mods:
        if char not in MODIFIERS.keys():
            invalidModifier(char, mods)
    return mods


def validate_to_opts(string: str) -> str:
    """
    Check that the optional modifier is valid. This function is only called
    if the UserMapping object has an 'opts' attribute, which is only set
    if the user added a to_opts argument in the correct position in a map.
    """
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
