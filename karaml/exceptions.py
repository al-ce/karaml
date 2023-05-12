from sys import exit
import karaml.cfg


def configError(string: str):
    print("Error in config file:\n")
    if karaml.cfg.debug_flag:
        raise Exception(string)
    else:
        print(string)
        exit()


def invalidConditionValue(name: str, value: str):
    configError(
        f"Invalid value for condition: {name}={value}.\n"
        "Value must be int type 0 or 1.\n"
        f"Got: {value} of type {type(value)}"
    )


def invalidFrontmostAppCondition(condition: str, map_rhs: dict):
    configError(
        "Invalid condition for frontmost_application\n"
        "Key must be either 'if' or 'unless'\n"
        f"Got: {condition}\nIn:\n{map_rhs}"
    )


def invalidKey(key_type: str, map: str, key: str):
    key_type = "modifier" if key_type == "mod" else "key code"
    configError(f"Invalid user-defined {key_type} in map {map}: {key}")


def invalidDictFormatInString(string: str, note: str):
    """
    User intended to pass a dict as an arg to a template, but the dict
    is not well formed.
    """

    configError(
        f"Invalid dict format in string:\n\n{string}\n\n"
        "Dicts must be have a colon separating their keys and values,\n"
        "and a comma separating each key-value pair.\n"
        f"{note}\n"
    )


def invalidToModType(usr_to_map: str):
    configError(f"'optional' not allowed for 'to.modifiers': {usr_to_map}")


def invalidFlag(string: str):
    configError(
        f"Bool flag for opts must be `+` or `-`, got `{string[0]}`: {string}")


def invalidLayerName(string: str):
    configError(
        f"Invalid layer name: {string}. "
        "Layer names must be in the form `/layer_name/`"
    )


def invalidToOpt(string: str):
    configError(
        f"Valid opts: 'lazy', 'repeat', got {string[1:]}: {string}")


def invalidSHNotifyDict(string: str, key: str):
    configError(
        f"Invalid key for shnotify() dict:\n  {string}\n"
        "Valid keys include:\n"
        "- title\n"
        "- subtitle\n"
        "- message\n"
        "- sound\n\n"
        f"Invalid key: {key}"
    )


def invalidModifier(string: str, mods: str):
    configError(
        f"Invalid modifier: {string}\nIn mod string: {mods}\n"
        "Valid modifiers are:\n\n"
        "  - left_control, left_shift, left_option, left_command\n"
        "  - right_control, right_shift, right_option, right_command\n"
        "  - control, shift, option, command\n"
        "  - fn, caps_lock"
    )


def invalidMousePosArgs(mouse_pos_args: str, msg: str):
    configError(
        f"Invalid mouse position arguments: {mouse_pos_args}\n"
        f"{msg}"
    )


def invalidTotalParensInMods(mod_string: str, opt_mod_matches: list):
    configError(
        f"Invalid optional modifier mapping: {mod_string}\n"
        f"For opt mods: {opt_mod_matches}\n"
        "Too many sets of parens for optional mods. Use a single set.\n"
        "Put the optional mods entirely to the left or right.\n"
        "e.g. c(oms) or (c)oms or <c(oms)> or <(c)oms>\n"
        "NOT: c(o)(m)s or (o)(m)s or <c(om)s> etc."
    )


def invalidParamKeys(param_dict: dict, key: str):
    configError(
        f"Invalid parameter dict: `{key}`"
        "Valid keys include:\n"
        "- basic.to_if_alone_timeout_milliseconds\n"
        "- basic.to_if_held_down_threshold_milliseconds\n"
        "- basic.to_delayed_action_delay_milliseconds\n"
        "- basic.simultaneous_threshold_milliseconds\n"
        "- mouse_motion_to_scroll.speed\n"
        "Valid aliases for these keys are: a, h, d, s, m\n"
        "Got:\n"
        f"{param_dict}\n"
        f"Invalid key: {key}"
    )


def invalidParamValues(param_dict: dict, value: int):
    configError(
        "Invalid parameter dict. All values must be integers.\n"
        "From the param dict:\n"
        f"{param_dict}\n"
        f"Invalid value: {value} of type {type(value)}"
    )


def invalidSoftFunct(string: str):
    "Invalid software function argument: need well formed dict. Got:"
    f" {string}"


def invalidStickyModValue(string: str):
    configError(
        f"Invalid sticky modifier value: {string}. "
        "Must be 'on', 'off', or 'toggle'"
    )


def invalidStickyModifier(string: str):
    configError(
        f"Invalid modifier: {string}"
        f"Valid modifiers are:\n"
        "left_control, left_shift, left_option, left_command, right_control, "
        "right_shift, right_option, right_command, fn"
    )


def invalidUserDefinedAlias(alias_def: str, invalid_string: str):
    """
    Raises an error that the user has either specified too many items in a
    user-defined alias or that the items are not of the correct type.

    Args:
        alias_def (str): The target of the user-defined alias.
        invalid_string (str): The invalid string that was passed.
    """
    configError(
        "A user-defined primary alias should have the form:\n"
        "alias: {modifiers (optional)} {delimiter} {key code}\n\n"
        "Got:\n"
        f"{alias_def}"
        f"\n\nInvalid string:\n"
        f"{invalid_string}"
    )


def missingToMap(from_map: str):
    configError(f"Must map 'to' key for: {from_map}")
