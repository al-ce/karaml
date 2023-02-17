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


def modifier_lookup(usr_mods: list) -> list:
    return [MODIFIERS.get(mod) for mod in usr_mods if MODIFIERS.get(mod)]


def is_modded_key(string: str):
    expr = "<(.+)-(.+)>"

    if query := search(expr, string):
        ModifiedKey = namedtuple("ModifiedKey", ["modifiers", "key"])
        return ModifiedKey(*query.groups())


def is_dict(obj):
    return isinstance(obj, dict)


def is_layer(string: str):
    if layer := search("/(\\w+)/", string):
        return layer.group(1)


def get_multi_keys(string: str):
    if "+" in string:
        return string.split("+")


def parse_chars_in_parens(string: str):
    in_parens = search(r"\((.*?)\)", string)
    not_in_parens = search(r"[\w+]+(?![^()]*\))", string)
    in_parens = list(in_parens[0]) if in_parens else in_parens
    not_in_parens = list(not_in_parens[0]) if not_in_parens else not_in_parens
    return not_in_parens, in_parens
