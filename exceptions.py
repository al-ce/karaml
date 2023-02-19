def invalidKey(key_type: str, map: str, key: str):
    key_type = "modifier" if key_type == "mod" else "key code"
    return f"Invalid user-defined {key_type} in map {map}: {key}"


def invalidToModType(usr_to_map: str):
    raise Exception(f"'optional' not allowed for 'to.modifiers': {usr_to_map}")


def invalidFlag(string: str):
    raise Exception(
        f"Bool flag for opts must be `+` or `-`, got `{string[0]}`: {string}")


def invalidOpt(string: str):
    raise Exception(
        f"Valid opts: 'halt', 'lazy', 'repeat', got {string[1:]}: {string}")
