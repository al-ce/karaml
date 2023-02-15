from re import search
from collections import namedtuple
from itertools import chain


def invalidKey(key_type: str, map: str, key: str):
    key_type = "modifier" if key_type == "mod" else "key code"
    return f"Invalid user-defined {key_type} in map {map}: {key}"


def invalidModifierRule(usr_from_map: str):
    return f"Invalid modifier rule for {usr_from_map}. Must use " \
        "'< >' for mandatory, '( )' for optional modifiers"


def all_in(items: list, container: iter) -> bool:
    for item in items:
        if item not in container:
            return False
    return True


def filter_list(unfiltered):
    return list(chain.from_iterable([x for x in unfiltered if x]))


def make_list(x) -> list:
    return [x] if not isinstance(x, list) else x


def is_modded_key(string):
    expr = "(\\w+)-([^)>]+)"
    if query := search(expr, string):
        ModifiedKey = namedtuple("ModifiedKey", ["modifier", "key"])
        return ModifiedKey(*query.groups())


def is_dict(obj):
    return isinstance(obj, dict)


def is_layer(string):
    if layer := search("/(\\w+)/", string):
        return layer.group(1)


def get_multi_keys(string):
    expr = "\\(([^,]+.*)\\)"
    if search(expr, string):
        return string[1:-1].split(",")


def validate_modifier_rules(usr_from_map: str):
    if all_in(["<", ">"], usr_from_map):
        return "mandatory"
    elif all_in(["(", ")"], usr_from_map):
        return "optional"
    raise Exception(invalidModifierRule(usr_from_map))
