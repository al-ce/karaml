import re
from itertools import chain
from string import ascii_letters, ascii_uppercase, digits, punctuation

import pytest
from testing_assets import KEYCODE_COMBINATIONS

import karaml.helpers as helpers
import karaml.map_translator as mp
from karaml.key_codes import ALIASES, KEY_CODE, MODIFIERS
from karaml.map_translator import KeyStruct, ModifiedKey, TranslatedMap


def test_TranslatedMap():

    events = 'open(https://github.com)'
    layers = '/sys/'

    samples = KEYCODE_COMBINATIONS + [events, layers]

    sampleTranslatedMaps = [TranslatedMap(key) for key in samples]
    for keys_list in sampleTranslatedMaps:
        assert type(keys_list.keys) == list
        # TranslatedMap generates KeyStructs from its args in all sample cases
        for keystruct in keys_list.keys:
            assert type(keystruct) == KeyStruct


def test_is_modded_key():
    valid_modified_keys = [
        "<mods-primary>",
        "mods-primary",
        "mods|primary",
        "mods | primary",
        " <mods-primary> ",
        " mods-primary ",
        " mods|primary ",
        " mods | primary ",
        "mods primary",
        "m o d s | primary",
        "m o d s primary",
        "m o  d  s  primary",
    ]
    invalid_modified = [
        "mods:primary",
        "<modsprimary>",
        "primary",
    ]

    for valid in valid_modified_keys:
        valid_ModifiedKey: ModifiedKey = mp.is_modded_key(valid)
        assert valid_ModifiedKey
        assert type(valid_ModifiedKey) == ModifiedKey
        assert valid_ModifiedKey.modifiers == "mods"
        assert valid_ModifiedKey.key == "primary"

    for inv_mod in invalid_modified:
        assert not mp.is_modded_key(inv_mod)


def test_validate_mods():
    mods = list(MODIFIERS.keys())
    double_mods = [f"{m}{n}" for m in mods for n in mods if m != n]
    opt_mods = [f"({m})" for m in mods]
    mandatory_opt_right = [f"{m}({n})" for m in mods for n in mods if m != n]
    mandatory_opt_left = [f"({m}){n})" for m in mods for n in mods if m != n]
    mandatory_opt_middle = [
        f"{m}({n}){p}"
        for m in mods
        for n in mods
        for p in mods
        if m != n and n != p
    ]
    other_cases = ["scmo", "SCMO", "sCmO", "grahGRAH", "flFL", "a(x)rGc"]

    sample_valid_mods = mods + double_mods + opt_mods + mandatory_opt_right + \
        mandatory_opt_left + mandatory_opt_middle + other_cases

    for mod_str in sample_valid_mods:
        validated_mod = helpers.validate_mod_aliases(mod_str)
        assert validated_mod
        assert isinstance(validated_mod, str)
        assert "(" not in validated_mod
        assert ")" not in validated_mod

    # Only chars in mod alias list. Also, modifiers should be separated from
    # its primary key before arriving at this function
    sample_invalid_mods = [
        char for char in ascii_letters if char not in mods
    ] + ["<c-j>"]

    for mod_str in sample_invalid_mods:
        with pytest.raises(SystemExit) as inv_mod_test:
            validated_mod = helpers.validate_mod_aliases(mod_str)
        assert inv_mod_test.type == SystemExit


def test_parse_chars_in_parens():
    sample_mods = ["c", "(c)", "cs", "(cs)", "c(x)", "(x)c"]
    for mod in sample_mods:
        # mandatory, optional are named not_in_parens, in_parens in the func
        mandatory, optional = mp.parse_chars_in_parens(mod)

        if "(" in mod or ")" in mod:
            assert optional
            start, end = mod.find("("), mod.find(")")
            # All chars in the list joned are the same as the first set of
            # chars in parens
            assert "".join(optional) == mod[start+1:end]
        else:
            assert mandatory
            assert not optional

    with pytest.raises(SystemExit) as inv_mod_test:
        # Optional mods in parens must be either to the left or right of
        # all mandatory mods
        mp.parse_chars_in_parens("c(x)s")
    assert inv_mod_test.type == SystemExit


def test_modifier_lookup():
    mod_aliases = MODIFIERS.keys()
    assert mp.modifier_lookup(mod_aliases)
    # A letter that's not a valid modifier alias will not return a modifier
    # key_code
    assert not mp.modifier_lookup(["j"])


def test_get_modifiers():
    valid_mods = mp.get_modifiers("cs(x)", "<cs(x)-j>")

    assert type(valid_mods) == dict
    assert valid_mods["mandatory"] == ["left_control", "left_shift"]
    assert valid_mods["optional"] == ["any"]

    with pytest.raises(SystemExit) as inv_mod_aliases_test:
        # Invalid mod aliases won't be accepted
        mp.get_modifiers("jkz", "<jkz-j>")
    assert inv_mod_aliases_test.type == SystemExit

    with pytest.raises(SystemExit) as inv_opt_mods_test:
        # Optional mods must be to the left or right of any mandatory mods
        mp.get_modifiers("c(s)o", "<cso-j>")
    assert inv_opt_mods_test.type == SystemExit


def test_parse_primary_key_and_mods():
    modded = "<cs-j>"
    no_mods = "j"

    modded_key, modifiers = mp.parse_primary_key_and_mods(modded, modded)
    no_mod_key, none_type = mp.parse_primary_key_and_mods(no_mods, no_mods)
    assert isinstance(modded_key, str)
    assert isinstance(modifiers, dict)
    assert modded_key == "j"
    assert modifiers["mandatory"] == ["left_control", "left_shift"]

    assert isinstance(no_mod_key, str)
    # If there are no modifiers, the function returns an empty dict
    assert not none_type
    assert no_mod_key == "j"


def test_is_layer():
    valid_layer = "/nav/"
    valid_check = mp.translate_if_layer(valid_layer)
    assert isinstance(valid_check, KeyStruct)
    assert valid_check.key_type == "layer"
    assert valid_check.key_code == "nav"
    assert not valid_check.modifiers

    invalid_layers = ["nav", "/nav", "nav/", "x/nav/", "/nav/x"]
    for inv in invalid_layers:
        assert not mp.translate_if_layer(inv)


def test_special_to_event_check():
    # Checks for special events, not regular keycodes
    assert not mp.translate_if_template("j")

    se_case = mp.translate_if_template("app(Firefox)")
    assert isinstance(se_case, KeyStruct)
    assert se_case.key_code == "open -a 'Firefox'.app"
    assert se_case.key_type == "shell_command"
    assert not se_case.modifiers

    # Special events need to be in the form of 'event(arg)'
    assert not mp.translate_if_template("app")
    assert not mp.translate_if_template("app()")
    # And must be valid special events, not just some_string(arg)
    assert not mp.translate_if_template("some_string(arg)")


def test_resolve_alias():

    shift_requiring_aliases = [
        alias for alias in ALIASES.keys()
        # FIX: doesn't account for mutlimod aliases e.g. hyper
        if ALIASES[alias].modifiers == ["shift"]
    ] + list(ascii_uppercase)

    for aliased_map, alias_named_tuple in ALIASES.items():
        mod_dict = {"mandatory": ["left_control"], "optional": ["fn"]}
        valid_alias = mp.resolve_alias(aliased_map, "alias", ALIASES, mod_dict)
        assert valid_alias
        assert isinstance(valid_alias, KeyStruct)
        assert valid_alias.key_type == "key_code"
        assert valid_alias.key_code == alias_named_tuple.key_code

        if aliased_map in shift_requiring_aliases:
            assert valid_alias.modifiers == {
                "mandatory": ["left_control", "shift"],
                "optional": ["fn"]
            }
        else:
            assert valid_alias.modifiers == mod_dict


def test_is_valid_keycode():

    typical_cases_list = [
        list(KEY_CODE),
        [f"<{m}-{k}>" for m in MODIFIERS for k in KEY_CODE],
        [f"<{m}({o})-j>" for m in MODIFIERS for o in MODIFIERS],
        ["<coms(x)-j>", "<(x)coms-j>", "<F-F>", '"', "~", "<g-~>", "escape",
         "<s-escape>"]
    ]
    typical_cases = chain.from_iterable(typical_cases_list)
    dummy_usr_map = "<< this is a dummy user map for testing >>"
    "case of an Exception"

    for usr_key in typical_cases:
        valid_key_code = mp.translate_if_valid_keycode(usr_key, dummy_usr_map)
        assert isinstance(valid_key_code, KeyStruct)

        primary_key = re.search("[^>]+", usr_key.split("-")[-1]).group()
        if alias := ALIASES.get(primary_key):
            primary_key = alias.key_code
        assert valid_key_code.key_code == primary_key

        assert valid_key_code.key_type == "key_code"

    pointing_button_cases = ["button1", "<c-button1>", "<coms(x)-button1>"]
    for usr_key in pointing_button_cases:
        valid_pointing_button = mp.translate_if_valid_keycode(
            usr_key, dummy_usr_map)
        assert isinstance(valid_pointing_button, KeyStruct)
        assert valid_pointing_button.key_code == "button1"
        assert valid_pointing_button.key_type == "pointing_button"

    consumer_key_cases = ["al_terminal_lock_or_screensaver",
                          "<c-al_terminal_lock_or_screensaver>",
                          "<coms(x)-al_terminal_lock_or_screensaver>"]

    for usr_key in consumer_key_cases:
        valid_consumer_key = mp.translate_if_valid_keycode(
            usr_key, dummy_usr_map)
        assert isinstance(valid_consumer_key, KeyStruct)
        assert valid_consumer_key.key_code == "al_terminal_lock_or_screensaver"
        assert valid_consumer_key.key_type == "consumer_key_code"


def test_key_code_translator():

    valid_usr_maps = [
        "j",
        "<c-j>",
        "<c(o)-j>",
        "app(Firefox)",
        "left_shift",
        "button1",
        "al_terminal_lock_or_screensaver",
    ] + list(ALIASES.keys())

    for sample in valid_usr_maps:
        sampleTranslated = mp.key_code_translator(sample, sample)
        assert isinstance(sampleTranslated, KeyStruct)

    # Combinations (j+k) should be split up before being passed to this func
    # Invalid modifiers, optional modifier placement, invalid special events,
    # invalid keycodes, etc. should be caught before this func returns
    invalid_usr_maps = [
        "j+k", "<v-j>", "<c(o)s-j>", "app()", "Insert"
    ]

    for sample in invalid_usr_maps:
        with pytest.raises(SystemExit) as inv_usr_map_test:
            mp.key_code_translator(sample, sample)
        assert inv_usr_map_test.type == SystemExit


def test_queue_translations():
    simple = TranslatedMap("j")
    simul = TranslatedMap("j+k")

    assert len(mp.queue_translations(simple.map)) == 1
    assert len(mp.queue_translations(simul.map)) == 2


def test_get_multi_keys():

    for case in KEYCODE_COMBINATIONS:
        multi_keys = helpers.get_multi_keys(case)
        if '+' not in case:
            assert not multi_keys
        elif '+' in case:
            assert isinstance(multi_keys, list)
            assert len(multi_keys) >= 2


def test_string_pfunc():

    def check_keystruct_matches_char(word: str):
        string_event = f'string({word})'
        keystruct_list = mp.string_template(string_event)
        for i, keystruct in enumerate(keystruct_list):
            if word[i] in ALIASES.keys():
                assert keystruct.key_code == ALIASES[word[i]].key_code
            else:
                assert keystruct.key_code == word[i]
    word_lists = [
        list(ascii_letters),
        list(digits),
        list(punctuation),
        [key_code.key_code
         for alias, key_code in ALIASES.items()
         if len(alias) == 1]
    ]
    combined = list(chain.from_iterable(word_lists))
    combined.remove('+')  # since we use it for concatenation
    for char in combined:
        check_keystruct_matches_char(char)


def test_multiple_shell_cmds():
    """
    Test whether multiple shell commands in a single mapping, e.g.

    <gahr-8>: shell(open ~/.config/) + shell(open ~/Applications/)

    are concatenated into a single shell command, e.g.

    "to": [
        {
            "shell_command": "open ~/.config/ && open ~/Applications/"
        }
    ],
    """

    usr_key = "shell(open ~/.config/) + shell(open ~/Applications/) + <c-escape>"

    translations = mp.queue_translations(usr_key)

    # The two shell commands should be concatenated into a single shell command
    # held in one KeyStruct, so the length of the list should be 2
    assert len(translations) == 2

    # The first item in the list should be a KeyStruct with the escape key_type
    # The last item in the list should be a KeyStruct with the shell_command
    # key_type attribute (since we're appending the unified shell command last
    # after going through all the events in the mapping)
    escape_mapping = translations[0]
    assert escape_mapping.key_type == "key_code"
    assert escape_mapping.key_code == "escape"
    shell_cmd = translations[-1]
    assert shell_cmd.key_type == "shell_command"

    # The shell command should be a string with the two shell commands
    # concatenated with an && operator and surrounding whitespace
    assert shell_cmd.key_code == "open ~/.config/ && open ~/Applications/"

    # The escape KeyStruct should have a "modifiers" attribute with the
    # "mandatory" key set to ["left_control"]
    assert escape_mapping.modifiers["mandatory"] == ["left_control"]
    # The shell command KeyStruct's modifiers attribute should be empty
    assert shell_cmd.modifiers is None, f"Expected None, got {shell_cmd.modifiers}"
