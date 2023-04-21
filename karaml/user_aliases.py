from re import search

from karaml.helpers import validate_alias_key_code
from karaml.key_codes import (
    Alias,
    ALIASES,
    MODIFIER_ALIASES,
    MODIFIERS,
    PSEUDO_FUNCS,
)
from karaml.map_translator import parse_primary_key_and_mods


def update_user_aliases(d: dict) -> None:
    """
    Checks the top-level key "aliases" for a dict of user-defined
    aliases. Each alias key should have a valueof  a list with two to three
    items:
    - a string representing a valid key code
    - a list of strings representing valid modifier key codes
    - an optional third string defining the type of key code. If this field
        is left blank, the key code will be treated as a key_code type. For
        consumer_key_code and pointing_button types, the user should specify
        this third item

    This function calls functions that update the ALIASES dict with the
    user-defined aliases, as well as the MODIFIER_ALIASES dict if the
    alias definition includes only modifiers.

    The "aliases" key is popped from the imported YAML dict after updating
    the ALIASES dict.

    Returns None.
    """
    if not d.get("aliases"):
        return
    aliases = d.get("aliases")

    for alias, alias_def in aliases.items():
        alias_codes = process_alias_definition(alias, alias_def)
        alias_primary_key_code, mod_key_codes = alias_codes

        ALIASES[alias] = Alias(alias_primary_key_code, mod_key_codes)

        add_modifier_alias(alias, alias_def)

    d.pop("aliases")


def process_alias_definition(

    alias: str,
    alias_def: str
) -> tuple[str, str | None]:
    """
    Processes an alias definition to determine the primary key code and the
    optional modifiers, if any. If the alias definition is a
    pseudo-function, the primary key code is the entire alias definition
    string.

    Updates the ALIASES dict, and, if the alias definition is composed
    entirely of valid modifiers, adds the alias to the MODIFIER_ALIASES
    dict so they can be used in the "mandatory" and "optional" fields of
    a rule.

    Returns a tuple of the primary key code and the optional modifiers.
    """
    found_pf = search(r"^(\w+)\(.*\)$", alias_def)
    if found_pf and found_pf.group(1) in PSEUDO_FUNCS:
        return found_pf.group(), None

    primary_kc, alias_mods = parse_primary_key_and_mods(
        alias_def, f"{alias}: {alias_def}"
    )

    if modifier_in_primary := ALIASES.get(primary_kc):
        alias_primary_key_code = modifier_in_primary.key_code
    else:
        alias_primary_key_code = MODIFIERS.get(primary_kc) or primary_kc

    mod_key_codes = alias_mods.get("mandatory")
    if opt_mods := alias_mods.get("optional"):
        mod_key_codes += opt_mods

    validate_alias_key_code(alias_primary_key_code)
    return alias_primary_key_code, mod_key_codes


def add_modifier_alias(alias: str, alias_def: str) -> None:
    """
    Checks if all the key codes in the alias definition are valid modifier
    key codes. If so, adds the alias to the MODIFIER_ALIASES dict.

    Returns None.
    """
    alias_def_items = alias_def.split()
    new_mod_alias_value = ""
    for item in alias_def_items:
        if item not in MODIFIER_ALIASES and item not in MODIFIERS:
            return
        elif item in MODIFIERS:
            new_mod_alias_value += item
        elif item in MODIFIER_ALIASES:
            new_mod_alias_value += MODIFIER_ALIASES[item]

    MODIFIER_ALIASES[alias] = new_mod_alias_value
