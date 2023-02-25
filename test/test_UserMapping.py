from karaml.helpers import make_list
from karaml.key_karamlizer import UserMapping, KaramlizedKey


def make_test_maps():
    test_maps = {
        "simple_map": {
            "caps_lock": "escape"
        },
        "tap_and_hold_map": {
            "caps_lock": ["escape", "/nav/"]
        },
        "tap_hold_release_map": {
            "caps_lock": ["escape", "/nav/", "notify('/nav/ off)"]
        },
        "hold_only_map": {
            "caps_lock": [None, "/nav/"]
        },
        "release_only_map": {
            "caps_lock": [None, None, "notify('/nav/ off)"]
        },
        "fully_loaded_map": {
            "caps_lock": [
                "escape", "/nav/", "notify('/nav/ off)", ["+lazy"], {"a": 200}
            ]
        }
    }

    return test_maps


def test_UserMapping():

    test_maps = make_test_maps()

    for test_map in test_maps.values():
        for from_key, to_maps in test_map.items():
            user_map = UserMapping(from_key, to_maps)
            user_map_to = user_map.to_maps

            # Test that from_key and to_maps params are set correctly
            assert user_map.from_maps == from_key
            assert user_map_to == to_maps

            # Test that make_list() is turning strs into lists
            to_maps, user_map_to = map(make_list, (to_maps, user_map_to))
            assert type(to_maps) == list and type(user_map_to) == list

            # Test that the attrs of the UserMapping instance are set in the
            # correct order
            correct_order = ["tap", "hold", "after", "opts", "rule_params"]
            for i, to_map in enumerate(to_maps):
                assert to_map == user_map.items[i]
                assert to_map == getattr(user_map, correct_order[i])

            # Ensure we populate the rest of the list with None if the user's
            # map has less than 5 items
            if len(user_map.items) > len(to_maps):
                for item in user_map.items[len(to_maps) + 1:]:
                    assert item is None
