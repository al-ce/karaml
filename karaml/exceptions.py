from sys import exit
import karaml.cfg


def configError(string: str):
    print("Error in config file:\n")
    if karaml.cfg.debug_flag:
        raise Exception(string)
    else:
        print(string)
        exit()


def invalidKey(key_type: str, map: str, key: str):
    key_type = "modifier" if key_type == "mod" else "key code"
    configError(f"Invalid user-defined {key_type} in map {map}: {key}")


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


def invalidOpt(string: str):
    configError(
        f"Valid opts: 'lazy', 'repeat', got {string[1:]}: {string}")


def invalidModifier(string: str, mods: str):
    configError(
        f"Invalid modifier: {string}\nIn mod string: {mods}\n"
        "Valid modifiers are:\n\n"
        "  - left_control, left_shift, left_option, left_command\n"
        "  - right_control, right_shift, right_option, right_command\n"
        "  - control, shift, option, command\n"
        "  - fn, caps_lock"
    )


def invalidParamKeys(param_dict: dict, key):
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


def invalidParamValues(param_dict: dict, value):
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


def missingToMap(from_map: str):
    configError(f"Must map 'to' key for: {from_map}")
