def invalidKey(key_type: str, map: str, key: str):
    key_type = "modifier" if key_type == "mod" else "key code"
    return f"Invalid user-defined {key_type} in map {map}: {key}"


def invalidToModType(usr_to_map: str):
    raise Exception(f"'optional' not allowed for 'to.modifiers': {usr_to_map}")


def invalidFlag(string: str):
    raise Exception(
        f"Bool flag for opts must be `+` or `-`, got `{string[0]}`: {string}")


def invalidLayerName(string: str):
    raise Exception(
        f"Invalid layer name: {string}. "
        "Layer names must be in the form `/layer_name/`"
    )


def invalidOpt(string: str):
    raise Exception(
        f"Valid opts: 'halt', 'lazy', 'repeat', got {string[1:]}: {string}")


def invalidParamKeys(param_dict: dict, key):
    raise Exception(
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
    raise Exception(
        "Invalid parameter dict. All values must be integers.\n"
        "From the param dict:\n"
        f"{param_dict}\n"
        f"Invalid value: {value} of type {type(value)}"
    )


def invalidStickyModValue(string: str):
    raise Exception(
        f"Invalid sticky modifier value: {string}. "
        "Must be 'on', 'off', or 'toggle'"
    )


def invalidStickyModifier(string: str):
    raise Exception(
        f"Invalid modifier: {string}"
        f"Valid modifiers are:\n"
        "left_control, left_shift, left_option, left_command, right_control, "
        "right_shift, right_option, right_command, fn"
    )


def missingToMap(from_map: str):
    raise Exception(f"Must map 'to' key for: {from_map}")
