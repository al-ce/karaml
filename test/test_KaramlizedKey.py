import re

import pytest

# TAP_TOGGLE_LAYER is a simple escape to /nav/ map, hence, tap to toggle /nav/
from testing_assets import FULL_CONFIG_KEYS

from karaml.helpers import get_multi_keys, validate_layer
from karaml.key_codes import KEY_CODE_REF_LISTS, MODIFIERS
from karaml.key_karamlizer import (
    KaramlizedKey,
    UserMapping,
    chatter_safeguard,
    from_simultaneous_dict,
    get_condition_dict,
    get_layer_toggle_dict,
    local_mods,
)

HOLD_FLAVOR = "to"


def test_validate_layer():
    assert validate_layer("/base/") == "base"


def test_karamlized_key_conditions_attr():

    for test_key in FULL_CONFIG_KEYS:
        assert isinstance(test_key.layer_name, str)
        layers = get_multi_keys(test_key.layer_name) or [test_key.layer_name]
        assert isinstance(layers, list)

        if test_key.layer_name == "/base/":
            continue

        # All non-base layer maps require their layer is enabled
        assert test_key.conditions["conditions"]

        for condition in test_key.conditions["conditions"]:
            assert isinstance(condition, dict)
            # layer name is well formed
            assert re.search("^\\w+_layer$", condition["name"])
            assert condition["type"] == "variable_if"
            # value is an int, not str
            assert isinstance(condition["value"], int)
            # value is 0 (off) or 1 (on)
            assert 0 <= condition["value"] <= 1


def test_get_condition_dict():
    valid_condition_dict_args = get_condition_dict("nav_layer", 1)
    assert isinstance(valid_condition_dict_args, dict)
    assert valid_condition_dict_args["name"] == "nav_layer"
    assert valid_condition_dict_args["type"] == "variable_if"
    assert valid_condition_dict_args["value"] == 1


def test_get_layer_toggle_dict():
    ltd = get_layer_toggle_dict("nav_layer", 1)
    assert isinstance(ltd, dict)
    set_var = ltd["set_variable"]
    assert set_var["name"] == "nav_layer"
    assert set_var["value"] == 1


def test_karamlized_key_layer_toggle_attr():

    tap_mapping = UserMapping("escape", "/nav/")
    tkk = KaramlizedKey(tap_mapping, "/base/", "to")
    assert tkk.layer_toggle == [("nav_layer", "to")]

    # If part of a tap/hold map, when-tapped event becomes 'to_if_alone'
    tap_mapping = UserMapping("escape", ["/nav/", "caps_lock"])
    tkk = KaramlizedKey(tap_mapping, "/base/", "to")
    assert tkk.layer_toggle == [("nav_layer", "to_if_alone")]

    # var() func does not get added to the toggle-off list
    tap_mapping = UserMapping("escape", "var(nav_layer, 1)")
    tkk = KaramlizedKey(tap_mapping, "/base/", "to")
    assert not tkk.layer_toggle

    tap_mapping = UserMapping("escape", ["var(nav_layer, 1)", "caps_lock"])
    tkk = KaramlizedKey(tap_mapping, "/base/", "to")
    assert not tkk.layer_toggle


def test_karamlized_from_attr():
    def um(from_keys: str): return UserMapping(from_keys, "/nav/")
    def sk(keys: str): return KaramlizedKey(um(keys), "/base/", "to")

    # Simple froms return simple dict
    sample_key = sk("escape")
    assert sample_key._from == {"from": {"key_code": "escape"}}

    # Simul froms return simul dict
    sample_key = sk("j+k")
    assert sample_key._from == {"from": {"simultaneous": [
        {"key_code": "j"}, {"key_code": "k"}]}}

    # + modifiers
    sample_key = sk("<G-j>+k")
    assert sample_key._from == {
        "from": {
            "simultaneous": [{"key_code": "j"}, {"key_code": "k"}],
            "modifiers": {"mandatory": ["command"]}
        }
    }

    # all key_types
    sample_key = sk("button1")
    assert sample_key._from == {"from": {"pointing_button": "button1"}}

    sample_key = sk("button1+k")
    assert sample_key._from == {"from": {"simultaneous": [
        {"pointing_button": "button1"}, {"key_code": "k"}]}}

    sample_key = sk("al_terminal_lock_or_screensaver")
    assert sample_key._from == {"from": {
        "consumer_key_code": "al_terminal_lock_or_screensaver"
    }}

    sample_key = sk("al_terminal_lock_or_screensaver+k")
    assert sample_key._from == {"from": {"simultaneous": [
        {"consumer_key_code": "al_terminal_lock_or_screensaver"},
        {"key_code": "k"}
    ]}}


def test_karamlized_to_attr():
    def um(to_keys: str): return UserMapping("caps_lock", to_keys)
    def sk(keys: str): return KaramlizedKey(um(keys), "/base/", "to")

    # Simple to event
    sample_key = sk("escape")
    assert sample_key._to == {"to": [{"key_code": "escape"}]}

    # Multiple to events
    sample_key = sk("j+k")
    assert sample_key._to == {
        "to": [{"key_code": "j"}, {"key_code": "k"}]
    }

    # Multiple to events with modifiers
    sample_key = sk("<G-j>+k")
    assert sample_key._to == {
        "to": [
            {"key_code": "j", "modifiers": ["command"]},
            {"key_code": "k"}
        ]}

    # Multiple to events in the when-held position (non-chatty keys)
    sample_key = sk(["escape", "left_shift+left_control"])
    assert sample_key._to == {
        "to_if_alone": [{"key_code": "escape"}],
        "to": [{"key_code": "left_shift"}, {"key_code": "left_control"}]
    }

    # Multiple to events in the when-held position (chatty keys)
    sample_key = sk(["escape", "j+k"])
    assert sample_key._to == {
        "to_if_alone": [{"key_code": "escape"}],
        "to_if_held_down": [{"key_code": "j"}, {"key_code": "k"}]
    }

    # Tap to toggle layer (corresponding toggle-off key is created later)
    sample_key = sk("/nav/")
    assert sample_key._to == {
        "to": [{"set_variable": {"name": "nav_layer", "value": 1}}]
    }

    # Layer enabled when-held, send some other key on tap.
    # Auto-creates when-released (to_after_key_up) map
    sample_key = sk(["escape", "/nav/"])
    assert sample_key._to == {
        "to": [{"set_variable": {"name": "nav_layer", "value": 1}}],
        "to_after_key_up": [{"set_variable": {
            "name": "nav_layer",
            "value": 0
        }}],
        "to_if_alone": [{"key_code": "escape"}]
    }

    # Enable layer when held, nothing on tap (actually does tap-toggle it
    # quickly but doesn't matter for our purposes)
    sample_key = sk([None, "/nav/"])
    assert sample_key._to == {
        "to": [{"set_variable": {"name": "nav_layer", "value": 1}}],
        "to_after_key_up": [{"set_variable": {
            "name": "nav_layer",
            "value": 0
        }}]
    }

    # Define when-held, when-released
    # Chatty keys need to be sent to the "to_if_held_down" dict, non-chatty
    # keys can stay in "to"

    # Chatty example
    sample_key = sk(
        ["escape", "button1+notify(id1,SomeMessage)", "notify(id1,)"])
    assert sample_key._to == {
        "to_if_held_down": [
            {"pointing_button": "button1"},
            {"set_notification_message": {"id": "id1", "text": "SomeMessage"}}
        ],
        "to_after_key_up": [
            {"set_notification_message": {"id": "id1", "text": ""}}
        ],
        "to_if_alone": [{"key_code": "escape"}]
    }

    # Non-chatty whe-held, when-relesed example
    # (notifications are not considered chatty)
    sample_key = sk([
        "escape",
        "<oms-left_control>+notify(ctrlid,Hyper Enabled)",
        "notify(ctrlid,)"
    ])
    assert sample_key._to == {
        "to": [
            {"key_code": "left_control",
             "modifiers": ["left_option", "left_command", "left_shift"]},
            {
                "set_notification_message": {
                    "id": "ctrlid",
                    "text": "Hyper Enabled"
                }
            }
        ],
        "to_after_key_up": [
            {"set_notification_message": {"id": "ctrlid", "text": ""}}
        ],
        "to_if_alone": [{"key_code": "escape"}]
    }


def test_chatter_safeguard():
    # The first argument of chatter_guard represents a key in the
    # 'when-held' position of a karaml map. For this test's purposes, we just
    # need to be True or False depending on what we're checking.
    # Chatty keys need to be sent to the "to_if_held_down" dict, non-chatty
    # keys can stay in "to"

    # Modifiers in a "to" event dict are not considered 'chatty'
    for mod in MODIFIERS.values():
        key_list = [{"key_code": mod}]
        assert chatter_safeguard(mod, key_list, "to") == "to"

        # This represents a layer toggle in the 'when-tapped' position, so
        # there's no need to prevent chatter, so it returns the same event
        for to_event in [
            "to", "to_if_alone", "to_after_key_up", "to_if_held_down"
        ]:
            assert chatter_safeguard(None, key_list, to_event) == to_event

    # Layers are not considered 'chatty'
    assert chatter_safeguard(
        "/nav/",
        [{'set_variable': {'name': 'nav_layer', 'value': 1}}], "to"
    ) == "to"

    # All key codes that aren't modifiers are considered chatty, including
    # pointing_button and consumer_key_code key codes
    for ref_tuple in KEY_CODE_REF_LISTS:
        key_type, ref_list = ref_tuple.key_type, ref_tuple.ref
        if key_type == "alias":
            continue
        for key_code in ref_list:
            if key_code in MODIFIERS.values():
                continue
            assert chatter_safeguard(
                "control",
                [{key_type: key_code}],
                "to"
            ) == "to_if_held_down"


def test_from_simultaneous_dict():
    mandatory_only = [
        {"key_code": "j", "modifiers": {"mandatory": ['left_shift']}},
        {"key_code": "k", "modifiers": {"mandatory": ['left_command']}},
    ]

    assert from_simultaneous_dict(mandatory_only) == {
        "simultaneous": [{"key_code": "j"}, {"key_code": "k"}],
        "modifiers": {"mandatory": ["left_shift", "left_command"]}
    }

    optional_only = [
        {"key_code": "j", "modifiers": {"optional": ['left_shift']}},
        {"key_code": "k", "modifiers": {"optional": ['left_command']}},
    ]

    assert from_simultaneous_dict(optional_only) == {
        "simultaneous": [{"key_code": "j"}, {"key_code": "k"}],
        "modifiers": {"optional": ["left_shift", "left_command"]}
    }

    mandatory_and_optional = [
        {"key_code": "j", "modifiers": {"mandatory": ['left_shift']}},
        {"key_code": "k", "modifiers": {"mandatory": ['left_command']}},
        {"key_code": "l", "modifiers": {"optional": ['left_control']}},
    ]

    assert from_simultaneous_dict(mandatory_and_optional) == {
        "simultaneous": [
            {"key_code": "j"}, {"key_code": "k"}, {"key_code": "l"}
        ],
        "modifiers": {
            "mandatory": ["left_shift", "left_command"],
            "optional": ["left_control"]
        }
    }

    # This function should raise an exception if it's passed a list with only
    # one event
    with pytest.raises(Exception) as single_event_test:
        from_simultaneous_dict(
            [{"key_code": "j", "modifiers": {"mandatory": ['left_shift']}}]
        )
    assert single_event_test.type == Exception


def test_local_mods():
    sample_UserMapping = UserMapping("caps_lock", ["escape", "/nav/"])

    assert isinstance(
        local_mods({"mandatory": "control"}, "some_event", sample_UserMapping),
        dict
    )

    # Returns an empty dict if it's passed an empty dict
    assert not local_mods({}, "some_event", sample_UserMapping)

    # prints error/raises Exception and exits if event is not "from" and there
    # are optional modifiers in the mods dict
    with pytest.raises(SystemExit) as invalid_opt_mods_in_to:
        local_mods({"mandatory": "control", "optional": ["left_shift"]},
                   "to",
                   sample_UserMapping)
    assert invalid_opt_mods_in_to.type == SystemExit

    # mods dict can have optional modifiers if event is "from"
    assert local_mods(
        from_mods := {"mandatory": "control",
                      "optional": ["left_shift"]},
        "from",
        sample_UserMapping) == {"modifiers": from_mods}
