from karaml.karaml_config import (
    KaramlConfig,
    get_app_conditions_dict,
    get_karamlized_key,
)
from karaml.key_codes import ALIASES, KEY_CODE
from karaml.key_karamlizer import KaramlizedKey, UserMapping

MIN_CONFIG_PATH = "./test/test_config_min.yaml"
FULL_CONFIG_PATH = "./test/test_config_full.yaml"
AUTO_TOGGLE_CONFIG_PATH = "./test/test_auto_toggle_config.yaml"
HOLD_FLAVOR = "to"

MIN_CONFIG_SAMPLE = KaramlConfig(MIN_CONFIG_PATH, HOLD_FLAVOR)
FULL_CONFIG_SAMPLE = KaramlConfig(FULL_CONFIG_PATH, HOLD_FLAVOR)
AUTO_TOGGLE_CONFIG_SAMPLE = KaramlConfig(AUTO_TOGGLE_CONFIG_PATH, HOLD_FLAVOR)


def make_keycode_combinations():
    simple = list(KEY_CODE)
    aliases = list(ALIASES)
    combos = [
        f"{x}+{y}"
        for x in KEY_CODE
        for y in KEY_CODE
        if x != y
    ]
    combos.append('j + k')
    combos.append('j+k')
    combos.append('j + k+l')
    return simple + aliases + combos


def make_sample_KaramlizedKeys(test_config):
    sample_yaml_data = test_config.yaml_data

    sample_karamlized_keys = []
    for layer_name, layer_maps in sample_yaml_data.items():
        for from_keys, rhs in layer_maps.items():
            gkk_args = [from_keys, layer_name, "to"]
            if type(rhs) in [list, str]:
                karamlized_key = get_karamlized_key(*gkk_args, rhs)
                sample_karamlized_keys.append(karamlized_key)

            # If this map is a dict of frontmost app based conditions
            elif isinstance(rhs, dict):
                # Append a modification for each condition
                for frontmost_app_key, to_keys in rhs.items():
                    karamlized_key = get_karamlized_key(*gkk_args, to_keys)
                    frontmost_app_dict = get_app_conditions_dict(
                        frontmost_app_key, rhs)
                    karamlized_key.conditions["conditions"].append(
                        frontmost_app_dict)
                    sample_karamlized_keys.append(karamlized_key)

    return sample_karamlized_keys


FULL_CONFIG_KEYS = make_sample_KaramlizedKeys(FULL_CONFIG_SAMPLE)
KEYCODE_COMBINATIONS = make_keycode_combinations()


TAP_TOGGLE_LAYER = KaramlizedKey(
    UserMapping("caps_lock", "/nav/"),
    "/base/",
    HOLD_FLAVOR
)


HOLD_TO_ENABLE_LAYER = KaramlizedKey(
    UserMapping("caps_lock", ["escape", "/nav/"]),
    "/base/",
    HOLD_FLAVOR
)
