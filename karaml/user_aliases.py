from re import search

from karaml.helpers import validate_alias_key_code
from karaml.key_codes import (
    ALIASES,
    MODIFIER_ALIASES,
    MODIFIERS,
    Alias,
)
from karaml.map_translator import parse_primary_key_and_mods
from karaml.templates import TEMPLATES


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
    aliases = d.get("aliases")
    if not aliases:
        return

    for alias_name, alias_def in aliases.items():
        alias_codes = process_alias_definition(alias_name, alias_def)
        alias_primary_key_code, mod_key_codes = alias_codes

        ALIASES[alias_name] = Alias(alias_primary_key_code, mod_key_codes)

        add_modifier_alias(alias_name, alias_def)

    d.pop("aliases")


def process_alias_definition(
    alias_name: str,
    alias_def: str
) -> tuple[str, str | None]:
    """
    Processes an alias definition to determine the primary key code and the
    optional modifiers, if any. If the alias definition is a template, the
    primary key code is the entire alias definition string.

    Updates the ALIASES dict, and, if the alias definition is composed
    entirely of valid modifiers, adds the alias to the MODIFIER_ALIASES
    dict so they can be used in the "mandatory" and "optional" fields of
    a rule.

    Returns a tuple of the primary key code and the optional modifiers.
    """
    template_pattern = search(r"^(\w+)\(.*\)$", alias_def)

    # TODO: if this is a string(), it needs to default to the shell_command
    # version of string(), since the default 'fast' version is a concatenation
    # of 'to:' events, which is not how aliases work
    # HACK: lets make a quick warning.
    if template_pattern and template_pattern.group(1) == "string":
        print(
            f"WARNING: {alias_name} is a string() template. "
            "Aliasing string() templates is not yet supported.\n"
            "Got:\n"
            f"\t{alias_name}: {alias_def}\n"
        )
        from sys import exit
        exit(1)

    if template_pattern and template_pattern.group(1) in TEMPLATES:
        return template_pattern.group(), None

    primary_kc, alias_mods = parse_primary_key_and_mods(
        alias_def, f"{alias_name}: {alias_def}"
    )

    alias_primary_key_code = (
        ALIASES.get(primary_kc) or
        MODIFIER_ALIASES.get(primary_kc) or
        # e.g. `s` counts as `left_shift` only if there's no
        # non-whitespace delimiter in the alias definition, else it's `s`
        MODIFIERS.get(primary_kc) if (
            MODIFIERS.get(primary_kc) and
            not search(r"[-|].+$", alias_def)
        ) else None or

        primary_kc
    )

    mod_key_codes = alias_mods.get("mandatory")
    if opt_mods := alias_mods.get("optional"):
        mod_key_codes += opt_mods

    validate_alias_key_code(alias_primary_key_code)
    return alias_primary_key_code, mod_key_codes


def add_modifier_alias(alias_name: str, alias_def: str) -> None:
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
        if item in MODIFIERS:
            new_mod_alias_value += item
        elif item in MODIFIER_ALIASES:
            new_mod_alias_value += MODIFIER_ALIASES[item]

    MODIFIER_ALIASES[alias_name] = new_mod_alias_value
