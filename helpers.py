from re import search
from collections import namedtuple


def exceptionWriter(key_type: str, map: str, key: str):
    """Return a string with a formatted error message indicating that the user
    set an invalid modifier or a string ."""
    key_type = "modifier" if key_type == "mod" else "key code"
    return f"Invalid user-defined {key_type} in map {map}: {key}"


def make_list(x) -> list:
    """Return a list with the argument object as its only element if the object
    is not already a list."""
    return [x] if not isinstance(x, list) else x


def get_modded_key(string):
    """Return a namedtuple with the modifier and key code as its attributes
    if a regex expression that checks for modifier codes matches the argument
    string."""
    if query := search("<(\\w+)-(\\w+)>", string):
        ModifiedKey = namedtuple("ModifiedKey", ["modifier", "key"])
        return ModifiedKey(*query.groups())


def get_layer(string):
    """Return a string with the layer name if a regex expression that checks
    for layer syntax matches the argument string."""
    if layer := search("/(\\w+)/", string):
        return layer.group(1)


def get_simultaneous_keys(string):
    if query := search("\\(([^)]+)\\)", string):
        return query.group(1).split(",")
