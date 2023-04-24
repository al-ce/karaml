import re
import pytest
from karaml.karaml_config import get_app_conditions_dict
import karaml.karaml_config as kc


from testing_assets import (
    MIN_CONFIG_SAMPLE, FULL_CONFIG_SAMPLE, AUTO_TOGGLE_CONFIG_SAMPLE,
)


def test_load_karaml_config():
    yaml_data = MIN_CONFIG_SAMPLE.yaml_data

    assert type(yaml_data) == dict
    assert yaml_data == {
        "/base/": {
            "caps_lock": ["escape", "/nav/", None, None, None],
        }
    }


def test_get_profile_name():
    min_profile_name = MIN_CONFIG_SAMPLE.profile_name
    full_profile_name = FULL_CONFIG_SAMPLE.profile_name
    assert not min_profile_name
    assert type(full_profile_name) == str
    assert full_profile_name == "Karaml TEST Config"


def test_get_title():
    min_title = MIN_CONFIG_SAMPLE.title
    full_title = FULL_CONFIG_SAMPLE.title

    # Since title is not defined in the min config,
    # it should default to "Karaml Rules"
    assert min_title == "Karaml Rules"
    # There is no "title" key in the min config yaml_data dict
    assert not MIN_CONFIG_SAMPLE.yaml_data.get("title")
    assert full_title == "KaramlTESTRules"
    # "title" is popped from the yaml_data dict to set the title attr
    assert not FULL_CONFIG_SAMPLE.yaml_data.get("title")


def test_get_params():
    min_params = MIN_CONFIG_SAMPLE.params
    full_params = FULL_CONFIG_SAMPLE.params

    assert not min_params

    fp = full_params.get("parameters")
    assert type(fp) == dict
    valid_keys = [
        "basic.to_if_alone_timeout_milliseconds",
        "basic.to_if_held_down_threshold_milliseconds",
        "basic.to_delayed_action_delay_milliseconds",
        "basic.simultaneous_threshold_milliseconds",
        "mouse_motion_to_scroll.speed",
    ]
    valid_aliases = ["a", "h", "d", "s", "m"]
    for key, value in fp.items():
        assert key in valid_keys or key in valid_aliases
        assert type(value) == int


def test_get_json_rules_list():
    min_json = MIN_CONFIG_SAMPLE.json_rules_list
    full_json = FULL_CONFIG_SAMPLE.json_rules_list

    assert not min_json
    assert type(full_json) == list
    for rule in full_json:
        # PyYAML should parse the json-style objects as dicts
        assert type(rule) == dict


def test_gen_layers():
    min_layers = MIN_CONFIG_SAMPLE.layers
    full_layers = FULL_CONFIG_SAMPLE.layers

    assert type(min_layers) == list
    assert type(full_layers) == list

    assert len(min_layers) == 1

    # gen_layers() should reverse the order of the layers, so /base/ is last
    # /JSON/, if present, should be first after the reversal
    assert min_layers[0]["description"] == "/base/ layer"
    assert min_layers[-1]["description"] == "/base/ layer"

    assert full_layers[0]["description"] == "/JSON/ layer"
    assert full_layers[-1]["description"] == "/base/ layer"

    for layer in full_layers:
        assert re.match(r"/.+/ layer", layer["description"])
        assert type(layer["manipulators"]) == list
        assert len(layer["manipulators"]) > 0


def count_rules_in_yaml_config(layer):
    rule_count = 0
    for layer_name, layer_maps in layer.items():
        # account for multiple layer conditions (e.g. /layer1/ + /layer2/)
        if layer_name.startswith("/") and layer_name.endswith("/"):
            rule_count += len(layer_maps)
    return rule_count


def test_insert_toggle_off():

    yaml_data = AUTO_TOGGLE_CONFIG_SAMPLE.yaml_data
    # Auto toggle config has one map in the base layer:
    # /base/:
    #   escape: /nav/

    mapping = yaml_data["/base/"]
    toggled_layer = mapping.get("escape")
    assert toggled_layer == "/nav/"

    written_rule_count = count_rules_in_yaml_config(yaml_data)
    assert written_rule_count == 1

    # The rule count in self.layers should be two, since the toggle-off rule
    # should be added automatically
    layers = AUTO_TOGGLE_CONFIG_SAMPLE.layers
    base_layer = layers[-1]
    manipulators = base_layer["manipulators"]
    assert len(manipulators) != written_rule_count
    assert len(manipulators) == 2

    layer_name = toggled_layer[1:-1] + "_layer"
    toggle_on_rule = manipulators[0]
    toggle_off_rule = manipulators[1]
    assert toggle_on_rule["conditions"][0]["name"] == layer_name
    assert toggle_on_rule["conditions"][0]["value"] == 0
    assert toggle_on_rule["conditions"][0]["type"] == "variable_if"
    assert toggle_on_rule["to"][0]["set_variable"]["name"] == layer_name
    assert toggle_on_rule["to"][0]["set_variable"]["value"] == 1
    # manipulators[1] is the auto-inserted toggle-off rule, which has the same
    # condition name as manipulator[0] but with a value of 1
    assert toggle_off_rule["conditions"][0]["name"] == layer_name
    assert toggle_off_rule["conditions"][0]["value"] == 1
    assert toggle_off_rule["conditions"][0]["type"] == "variable_if"
    assert toggle_off_rule["to"][0]["set_variable"]["name"] == layer_name
    assert toggle_off_rule["to"][0]["set_variable"]["value"] == 0


def test_get_app_conditions_dict():
    assert get_app_conditions_dict("if firefox$ kitty$", "dummy_rhs") == {
        "type": "frontmost_application_if",
        "bundle_identifiers": ["firefox$", "kitty$"]
    }

    # Only valid conditionals (if or unless) should be allowed
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        get_app_conditions_dict("ifff firefox kitty", "dummy_rhs")
    assert pytest_wrapped_e.type == SystemExit


def test_parse_layer_key():
    test_layer_keys = [
        "/base/",
        "/base/ description",
        "/layer name with spaces/",
        "/base/ description with spaces",
        "/layer name with spaces/ description",
    ]

    for layer_key in test_layer_keys:

        # This needs to be tested as (/.+/)(.*) rather than (/[^/]+/)(.*)
        # because the latter break up a multi-layer key like /nav/ + /sym/.
        # This will pass an invalid layer, but this should be caught by
        # the validate_layer_name() function

        expected = re.search(r"^(/.+/)(.*)", layer_key).groups()
        expected_name = expected[0].strip()
        expected_desc = expected[1].strip()
        if not expected_desc:
            expected_desc = f"{expected_name} layer"

        layer_name, layer_description = kc.parse_layer_key(
            layer_key)

        assert layer_name == expected_name
        assert layer_description == expected_desc

    invalid_layer_keys = [
        "base/",
        "/base",
        "base",
    ]

    for layer_key in invalid_layer_keys:
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            kc.parse_layer_key(layer_key)
        assert pytest_wrapped_e.type == SystemExit
