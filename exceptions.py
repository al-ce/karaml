def invalidKey(key_type: str, map: str, key: str):
    key_type = "modifier" if key_type == "mod" else "key code"
    return f"Invalid user-defined {key_type} in map {map}: {key}"


def invalidToModType(usr_to_map: str):
    raise Exception(f"Opt flag for 'to.modifiers' not allowed: {usr_to_map}")
