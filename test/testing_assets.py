from karaml.karaml_config import KaramlConfig
from karaml.key_codes import ALIASES, KEY_CODE
from karaml.key_karamlizer import KaramlizedKey, UserMapping

MIN_CONFIG_PATH = "./test/test_config_min.yaml"
FULL_CONFIG_PATH = "./test/test_config_full.yaml"
AUTO_TOGGLE_CONFIG_PATH = "./test/test_auto_toggle_config.yaml"
hold_flavor = "to"

MIN_CONFIG_SAMPLE = KaramlConfig(MIN_CONFIG_PATH, hold_flavor)
FULL_CONFIG_SAMPLE = KaramlConfig(FULL_CONFIG_PATH, hold_flavor)
AUTO_TOGGLE_CONFIG_SAMPLE = KaramlConfig(AUTO_TOGGLE_CONFIG_PATH, hold_flavor)


def make_keycode_combinations():
    simple = [key for key in KEY_CODE]
    aliases = [alias for alias in ALIASES]
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
        for from_keys, to_keys in layer_maps.items():
            user_map = UserMapping(from_keys, to_keys)
            key_tuple = KaramlizedKey(user_map, layer_name, "to")
            # Test the arguments are passed correctly
            assert key_tuple.usr_map == user_map
            assert key_tuple.layer_name == layer_name
            sample_karamlized_keys.append(key_tuple)
    return sample_karamlized_keys


FULL_CONFIG_KEYS = make_sample_KaramlizedKeys(FULL_CONFIG_SAMPLE)
KEYCODE_COMBINATIONS = make_keycode_combinations()


TAP_TOGGLE_LAYER = KaramlizedKey(
    UserMapping("caps_lock", "/nav/"),
    "/base/",
    hold_flavor
)


HOLD_TO_ENABLE_LAYER = KaramlizedKey(
    UserMapping("caps_lock", ["escape", "/nav/"]),
    "/base/",
    hold_flavor
)
