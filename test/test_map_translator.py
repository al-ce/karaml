from itertools import chain
import pytest
import re
from string import ascii_uppercase, ascii_letters, digits

import karaml.map_translator as mp
import karaml.helpers as helpers
from karaml.key_codes import ALIASES, KEY_CODE, MODIFIERS
from karaml.map_translator import KeyStruct, ModifiedKey, TranslatedMap

from testing_assets import KEYCODE_COMBINATIONS


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
    valid = "<mods-primary>"
    invalid_modified = [
        "mods-primary",
        "<modsprimary>",
        "<mods-primary",
        "mods-primary>",
    ]

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
        assert type(validated_mod) == str
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
    assert type(modded_key) == str
    assert type(modifiers) == dict
    assert modded_key == "j"
    assert modifiers["mandatory"] == ["left_control", "left_shift"]

    assert type(no_mod_key) == str
    # If there are no modifiers, the function returns an empty dict
    assert not none_type
    assert no_mod_key == "j"


def test_is_layer():
    valid_layer = "/nav/"
    valid_check = mp.translate_if_layer(valid_layer)
    assert type(valid_check) == KeyStruct
    assert valid_check.key_type == "layer"
    assert valid_check.key_code == "nav"
    assert not valid_check.modifiers

    invalid_layers = ["nav", "/nav", "nav/", "x/nav/", "/nav/x"]
    for inv in invalid_layers:
        assert not mp.translate_if_layer(inv)


def test_translate_event():

    # Not a special event, so nothing to translate
    assert mp.translate_pseudo_func("not_an_event", "some command") == (
        "not_an_event", "some command")

    assert mp.translate_pseudo_func("app", "Firefox") == (
        "shell_command", "open -a 'Firefox'.app")

    # We don't actually check what the command/argument for 'open()' or
    # 'shell()'_is (e.g. is it a valid link or command, etc.) & trust the user

    assert mp.translate_pseudo_func("open", "https://github.com") == (
        "shell_command", "open https://github.com"
    )

    assert mp.translate_pseudo_func("shell", "cd somedir/") == (
        "shell_command", "cd somedir/"
    )

    assert mp.translate_pseudo_func("input", "en") == (
        "select_input_source", {"language": "en"}
    )

    # TODO: add validation for select_input_source, mouse_key, soft_func,
    # etc. For now, it's the user's responsibility

    assert mp.translate_pseudo_func("input", "'{'some': 'dictionary'}'") == (
        "select_input_source", {"language": "'{'some': 'dictionary'}'"}
    )

    assert mp.translate_pseudo_func("mouse", "x, 2000") == (
        "mouse_key", {"x": 2000}
    )

    assert mp.translate_pseudo_func(
        "mouse",
        '''{
            "x": 2000,
            "y": 2000,
            "vertical_wheel": 2000,
            "horizontal_wheel": 2000,
            "speed_multiplier": 1.0
        }'''
    ) == (
        "mouse_key",

        {
            "x": 2000,
            "y": 2000,
            "vertical_wheel": 2000,
            "horizontal_wheel": 2000,
            "speed_multiplier": 1.0
        }
    )

    # Test for proper whitespace-stripping
    assert mp.translate_pseudo_func("notify", " some_id ,some_message") == (
        "set_notification_message", {"id": "some_id", "text": "some_message"}
    )

    assert mp.translate_pseudo_func("softFunc", "some_arg") == (
        "software_function", "some_arg"
    )

    sticky_values = ["on", "off", "toggle"]
    for v in sticky_values:
        assert mp.translate_pseudo_func("sticky", f"left_shift, {v}") == (
            "sticky_modifier", {"left_shift": v}
        )
    unsupported_sticky_mods = [
        "caps_lock", "command", "control", "option", "shift"
    ]
    with pytest.raises(SystemExit) as inv_sticky_mod_test:
        for m in unsupported_sticky_mods:
            # assert not mp.translate_event("sticky", f"{m}, on")
            mp.translate_pseudo_func("sticky", f"{m}, on")
    assert inv_sticky_mod_test.type == SystemExit

    # Only 'on', 'off', and 'toggle' are supported for sticky values
    with pytest.raises(SystemExit) as inv_sticky_val_test:
        mp.translate_pseudo_func("sticky", "left_shift, some_value")
    assert inv_sticky_val_test.type == SystemExit

    assert mp.translate_pseudo_func("var", "some_layer, 1") == (
        "set_variable", {"name": "some_layer", "value": 1}
    )

    with pytest.raises(SystemExit) as inv_var_value_type:
        mp.translate_pseudo_func("var", "some_layer, not_a_number")
    assert inv_var_value_type.type == SystemExit


def test_special_to_event_check():
    # Checks for special events, not regular keycodes
    assert not mp.translate_if_pseudo_func("j")

    se_case = mp.translate_if_pseudo_func("app(Firefox)")
    assert type(se_case) == KeyStruct
    assert se_case.key_code == "open -a 'Firefox'.app"
    assert se_case.key_type == "shell_command"
    assert not se_case.modifiers

    # Special events need to be in the form of 'event(arg)'
    assert not mp.translate_if_pseudo_func("app")
    assert not mp.translate_if_pseudo_func("app()")
    # And must be valid special events, not just some_string(arg)
    assert not mp.translate_if_pseudo_func("some_string(arg)")


def test_resolve_alias():

    shift_requiring_aliases = [
        alias for alias in ALIASES.keys()
        # FIX: doesn't account for mutlimod aliases e.g. hyper
        if ALIASES[alias].modifiers == ["shift"]
    ] + [letter for letter in ascii_uppercase]

    for aliased_map, alias_named_tuple in ALIASES.items():
        mod_dict = {"mandatory": ["left_control"], "optional": ["fn"]}
        valid_alias = mp.resolve_alias(aliased_map, "alias", ALIASES, mod_dict)
        assert valid_alias
        assert type(valid_alias) == KeyStruct
        assert valid_alias.key_type == "key_code"
        assert valid_alias.key_code == alias_named_tuple.key_code

        if aliased_map in shift_requiring_aliases:
            assert valid_alias.modifiers == {
                "mandatory": ["left_control", "shift"],
                "optional": ["fn"]
            }
            pass
        else:
            assert valid_alias.modifiers == mod_dict


def test_is_valid_keycode():

    typical_cases_list = [
        [k for k in KEY_CODE],
        [f"<{m}-{k}>" for m in MODIFIERS for k in KEY_CODE],
        [f"<{m}({o})-j>" for m in MODIFIERS for o in MODIFIERS],
        ["<coms(x)-j>", "<(x)coms-j>", "<F-F>", '"', "~", "<g-~>", "escape",
         "<s-escape>"]
    ]
    typical_cases = chain.from_iterable(typical_cases_list)
    dummy_usr_map = "The usr_map param is only passed through to give info in "
    "case of an Exception"

    for usr_key in typical_cases:
        valid_key_code = mp.translate_if_valid_keycode(usr_key, dummy_usr_map)
        assert type(valid_key_code) == KeyStruct

        primary_key = re.search("[^>]+", usr_key.split("-")[-1]).group()
        if alias := ALIASES.get(primary_key):
            primary_key = alias.key_code
        assert valid_key_code.key_code == primary_key

        assert valid_key_code.key_type == "key_code"

    poninting_button_cases = ["button1", "<c-button1>", "<coms(x)-button1>"]
    for usr_key in poninting_button_cases:
        valid_pointing_button = mp.translate_if_valid_keycode(usr_key, dummy_usr_map)
        assert type(valid_pointing_button) == KeyStruct
        assert valid_pointing_button.key_code == "button1"
        assert valid_pointing_button.key_type == "pointing_button"

    consumer_key_cases = ["al_terminal_lock_or_screensaver",
                          "<c-al_terminal_lock_or_screensaver>",
                          "<coms(x)-al_terminal_lock_or_screensaver>"]

    for usr_key in consumer_key_cases:
        valid_consumer_key = mp.translate_if_valid_keycode(usr_key, dummy_usr_map)
        assert type(valid_consumer_key) == KeyStruct
        assert valid_consumer_key.key_code == "al_terminal_lock_or_screensaver"
        assert valid_consumer_key.key_type == "consumer_key_code"


def test_key_code_translator():

    valid_usr_maps = ["j", "<c-j>", "<c(o)-j>", "app(Firefox)", "left_shift",
                      "button1", "al_terminal_lock_or_screensaver"] + [
        alias for alias in ALIASES.keys()
    ]

    for sample in valid_usr_maps:
        sampleTranslated = mp.key_code_translator(sample, sample)
        assert type(sampleTranslated) == KeyStruct

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
            assert type(multi_keys) == list
            assert len(multi_keys) >= 2


def test_multichar_func():

    def check_keystruct_matches_char(word: str):
        string_event = f'string({word})'
        keystruct_list = mp.multichar_func(string_event)
        for i, keystruct in enumerate(keystruct_list):
            if word[i] in ALIASES.keys():
                assert keystruct.key_code == ALIASES[word[i]].key_code
            else:
                assert keystruct.key_code == word[i]
    word_lists = [
        [c for c in ascii_letters],
        [d for d in digits],
        [key_code.key_code
         for alias, key_code in ALIASES.items()
         if len(alias) == 1]
    ]
    combined = list(chain.from_iterable(word_lists))
    for char in combined:
        check_keystruct_matches_char(char)

    some_phrase = "This string should include all letters, digits, and valid "
    "single char aliases (which means it can't include line breaks) "
    "1234567890 abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    "- _ = ()[]{}\\|;:'\"`~,<.>/?!@#$%^&*"

    check_keystruct_matches_char(some_phrase)
