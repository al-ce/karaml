import ast
from re import Match, search
from sys import exit as sys_exit

import yaml
from yaml import SafeLoader

from karaml.exceptions import (
    invalidConditionValue,
    invalidDictFormatInString,
    invalidFlag,
    invalidLayerName,
    invalidModifier,
    invalidMousePosArgs,
    invalidParamKeys,
    invalidParamValues,
    invalidSHNotifyDict,
    invalidStickyModifier,
    invalidStickyModValue,
    invalidToOpt,
    invalidTotalParensInMods,
)
from karaml.key_codes import (
    CONSUMER_KEY_CODE,
    KEY_CODE,
    MODIFIER_ALIASES,
    MODIFIERS,
    POINTING_BUTTON,
    STICKY_MODS,
)


def extract_yaml_node_value(mapping_node):
    """
    Gets the value of a YAML node representing either a single complex
    modification or a layer of complex modifications. This is used to
    print the key or layer that is being overwritten when a duplicate YAML key
    is found in the YAML file.
    If the node is a single complex modification, the value is the 'to' event/s
    of the complex modification.
    If the node is a layer, the value is the list of all the 'from' events
    of the complex modifications in the layer.
    """
    print("Value:")
    if not isinstance(mapping_node, yaml.nodes.MappingNode):
        print("    ", mapping_node.value)
        return mapping_node
    for key_node, _ in mapping_node.value:
        key = key_node.value
        print("    ", key)


class UniqueKeyLoader(SafeLoader):
    """
    This class inherits from the SafeLoader class of the PyYAML library.
    It overrides the compose_mapping_node method to check for duplicate
    keys in the YAML file.
    """

    def check_duplicate_keys(self, node):
        """
        Checks for duplicate keys in the YAML file. If a duplicate key is
        found, the key and the value of the key are printed to the console, and
        the warn_duplicate_key function is called to confirm that the user
        wants to overwrite the key.
        """
        keys = set()
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=False)
            if key in keys:
                print(f"Duplicate key found in YAML\n{key_node.start_mark}")
                print(f"\nKey: {key}")
                value_node = extract_yaml_node_value(value_node)
                warn_duplicate_key()
            keys.add(key)

    def compose_mapping_node(self, anchor):
        """
        Overloads the compose_mapping_node method of the SafeLoader class to
        check for duplicate keys in the YAML file.
        """
        node = super().compose_mapping_node(anchor)
        self.check_duplicate_keys(node)
        return node


def warn_duplicate_key():
    """
    Confirms that the user wants to overwrite a key that is already
    defined in the map. This is to prevent accidental overwrites.
    Continue to overwrite the key if the user confirms, else exit.
    """
    continue_check = input("""
This is a duplicate key in the same layer or a duplicate layer name.
This will overwrite the previous key or layer.

Do you want to continue? (y/n): """).lower()

    while continue_check not in ["y", "n"]:
        continue_check = input("Please enter 'y' or 'n': ").lower()
    if continue_check == "n":
        print("Exiting...")
        sys_exit()
    print()


def dict_eval(string: str) -> dict:
    """
    Returns a dict if the string is a valid dict, else returns an empty dict.
    """
    try:
        ast_dict = ast.literal_eval(string)
        return ast_dict if isinstance(ast_dict, dict) else {}
    except (ValueError, SyntaxError):
        return {}


def flag_check(string: str) -> bool:
    """
    Returns the value of the flag in the string for the to-event options
    'lazy' and 'repeat' after checking if the flag is valid. Otherwise, raise
    an exception and exit.
    """
    flags = {"+": True, "-": False}
    if (flag := string[0]) in flags:
        return flags[flag]
    invalidFlag(string)


def get_multi_keys(string: str) -> list[str]:
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
    return []


def is_layer(string: str) -> Match | None:
    """
    Returns True if the string matches the regex for an acceptable layer name.

    This function is used to determine what kind of to-event to assign the
    string to. If it is a layer, we might want to assign it to a 'to' event
    rather than a 'to_if_held_down' event so the layer can be accessed
    immediately without waiting for the 'to_if_held_down_threshold'.
    """
    return search("^/([^/]+)/$", string)


def validate_alias_key_code(alias_def: str) -> bool:
    """
    Returns a bool indicating if:
      - the alias definition is in one of the list of key code types:
        key_code, pointing_button, consumer_key_code, or a symbol alias for a
        modifier
    """
    return (
        isinstance(alias_def, str) and
        any(alias_def in x for x in (
            KEY_CODE,
            POINTING_BUTTON,
            CONSUMER_KEY_CODE,
            MODIFIER_ALIASES,
        ))
    )


def make_list(x) -> list:
    """
    Returns a list containing x if x is not a list, else returns the list x.
    The purpose of this function is to convert a single string to a list
    so it can be handled in the same way as a list of strings. In a karaml
    config, if a user's modification only has a single 'to' event, we do not
    want to make them wrap the string in a YAML list, so we do it for them.
    """
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
        if not isinstance(v, int):
            invalidParamValues(params, v)
    return {"parameters": translated} if translated else {}


def check_and_validate_str_as_dict(string: str) -> dict:
    """
    This function checks whether a string is intending to be in the form of a
    dict, and if it is, confirms that it is well-formed.
    This is used for templates like shnotify, mouse, input_source, etc.
    The string goes through a series of checks:

    1. The string must be enclosed in curly braces. This indicates that the
        user intends this arg to be evaluated as a dict.
        If this check doesn't pass, return False, indicating to the caller
        function that this arg is not intended to be a dict.
    2. The curly braces must enclose a valid set of key value pairs.
        This means that each comma-separated pair must be separated by a colon
        and that the keys must be strings. Hence the user needs to wrap the
        key in quotes.
    3. As a final dumb check, the string must evaluate to a dict without
        raising an error that this validation function isn't accounting for.

    If the last checks fail, the function will raise an error.
    Otherwise, it will return True.
    """

    if not string.startswith("{") or not string.endswith("}"):
        return {}

    kv_pairs = [
        pair.strip()
        for pair in string[1:-1].split(",")
        # Remove any empty strings that result from trailing commas
        if pair.strip()
    ]

    for pair in kv_pairs:
        k, _ = pair.split(":")
        k = k.strip()

        # The key might be a dict, so rerun this function on it
        # If it does not raise any errors, we can check the rest of the keys
        # in the main dictionary
        if k[0] == "{" and k[-1] == "}":
            check_and_validate_str_as_dict(k)
        elif k[0] not in ("'", '"') or k[-1] not in ("'", '"'):
            msg = f"Key '{k}' in dict '{string}' must be wrapped in quotes."
            invalidDictFormatInString(string, msg)
    try:
        if well_formed_dict := dict_eval(string):
            return well_formed_dict
        msg = f"karaml interpreted that\n\n{string}\n\nwas intended to" \
            " be a dict, but it failed to evaluate.\nPlease check" \
            " your syntax."
        invalidDictFormatInString(string, msg)
    except:  # noqa: E722
        # bad practice, but we will raise a useful Exception in this sequence
        # of function calls, and I'd rather warn the user with a generic
        # message than a misleading one
        msg = f"karaml interpreted that\n\n{string}\n\nwas intended to" \
            " be a dict, but it failed to evaluate.\nPlease check" \
            " your syntax."
        invalidDictFormatInString(string, msg)


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
            invalidSHNotifyDict(str(notification_dict), k)
            return


def validate_layer(string: str) -> str | None:
    """
    Returns the layer name if the string matches the regex for an acceptable
    layer name. Otherwise, it raises an error.

    The format must be a string enclosed in forward slashes, e.g. '/layer1/'
    with only alphanumeric characters and underscores.
    """
    layer: Match | None = is_layer(string)
    if not layer:
        invalidLayerName(string)
        return
    return layer.group(1) or invalidLayerName(string)


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


def validate_mouse_pos_args(mouse_pos_args: str) -> int:
    """
    Validates the arguments for the mousePos() templates.
    There must be at least two arguments and at most three arguments, and all
    must be integers. The first two arguments are the x and y coordinates of
    the mouse cursor, and the third argument is the screen number.
    """

    args = [arg.strip() for arg in mouse_pos_args.split(",")]
    if len(args) not in (2, 3) or not all(arg.isdigit() for arg in args):
        msg = "mousePos() takes 2 or 3 arguments, and all must be ints"
        invalidMousePosArgs(mouse_pos_args, msg)
    return 0



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
    """
    Check that if a user has added any optional modifiers to a map, they are
    formatted correctly. A correctly formatted modifier string will have only
    one set of parentheses containing the optional modifiers, and these must be
    either at the beginning or end of the string.
    """
    if len(opt_mod_matches) > 1 or search("\\w+\\(\\w+\\)\\w+", mod_string):
        invalidTotalParensInMods(mod_string, opt_mod_matches)


def validate_sticky_mod_value(string: str):
    """
    Check that the value for the sticky modifier modification is one of the
    three valid values: "on", "off", or "toggle".
    """
    if string not in ["on", "off", "toggle"]:
        invalidStickyModValue(string)


def validate_sticky_modifier(string: str):
    """
    Check that the sticky modifier is valid. Raises an error if it is not.

    As of KE 14.12.0, 'shift', 'control', 'option', and 'command' are not
    valid sticky modifiers.
    """
    if string not in STICKY_MODS:
        invalidStickyModifier(string)


def validate_var_value(name: str, value: str):
    """
    Check that the value for a variable is in integer form. Raises an error
    if it is not.
    """
    try:
        int(value)
    except ValueError:
        invalidConditionValue(name, value)
    if not 0 <= int(value) <= 1:
        invalidConditionValue(name, value)
