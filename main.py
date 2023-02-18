from collections import namedtuple
from dataclasses import dataclass
from json import dumps
from typing import Union
import yaml

from helpers import (
    condition_dict, dict_eval, invalidKey, invalidToModType, make_list,
    is_modded_key, is_layer, get_multi_keys, modifier_lookup,
    parse_chars_in_parens, requires_sublayer, toggle_layer_off, to_event_check,
)

from key_codes import KEY_CODE_REF_LISTS

KeyStruct = namedtuple("KeyStruct", ["key_type", "key_code", "modifiers"])


@dataclass
class UserMapping:

    from_keys: str
    maps: Union[str, list]

    def __post_init__(self):
        self.map_interpreter(self.maps)

    def map_interpreter(self, maps):
        maps = make_list(maps)
        [maps.append(None) for i in range(3-len(maps))]
        self.tap, self.hold, self.desc = maps

    def items(self):
        return self.tap, self.hold, self.desc


@dataclass
class MapTranslator:

    map: str

    def __post_init__(self):
        translated_keys = self.queue_translations(self.map)
        self.keys = translated_keys

    def queue_translations(self, parsed_key: str):
        if multi_keys := get_multi_keys(parsed_key):
            return [self.key_code_translator(k.strip()) for k in multi_keys]
        else:
            return [self.key_code_translator(parsed_key)]

    def key_code_translator(self, usr_key: str):

        if layer := is_layer(self.map):
            return layer

        if to_event := to_event_check(self.map):
            return to_event

        if keystruct := self.is_valid_keycode(usr_key):
            return keystruct

        raise Exception(invalidKey("key code", self.map, usr_key))

    def is_valid_keycode(self, usr_key):
        for ref_list in KEY_CODE_REF_LISTS:
            key_type, ref = ref_list.key_type, ref_list.ref
            parsed_key, modifiers = self.parse_modifiers(usr_key)

            if parsed_key not in ref:
                continue

            if dealiased_key := self.resolve_alias(parsed_key, key_type, ref):
                return KeyStruct("key_code", dealiased_key, modifiers)

            return KeyStruct(key_type, parsed_key, modifiers)

    def parse_modifiers(self, usr_key: str):
        if modified_key := is_modded_key(usr_key):
            return modified_key.key, self.get_modifiers(modified_key.modifiers)
        return usr_key, None

    def get_modifiers(self, usr_mods: str):
        mods = {}
        mandatory, optional = parse_chars_in_parens(usr_mods)
        if mandatory:
            mods["mandatory"] = modifier_lookup(mandatory)
        if optional:
            mods["optional"] = modifier_lookup(optional)

        if not mods:
            raise Exception(invalidKey("modifier", self.map, usr_mods))
        return mods

    def resolve_alias(self, usr_key: str, key_type: str, aliases_dict: dict):
        if key_type != "alias":
            return
        alias = aliases_dict[usr_key]
        return alias.key_code


@dataclass
class KaramlizedKey:

    usr_map: UserMapping
    layer_name: str

    def __post_init__(self):

        self.conditions = requires_sublayer(self.layer_name)
        self.layer_toggle = False

        desc = self.usr_map.desc
        self.desc = {"description": desc} if desc else None

        from_map = self.usr_map.from_keys
        self._from = {"from": self.from_keycode_localization(from_map)}

        self._to = {}
        tap_type = "to"
        if hold := self.usr_map.hold:
            self._to.update(self.to_keycodes_localization(hold, "to"))
            tap_type = "to_if_alone"
        if tap := self.usr_map.tap:
            self._to.update(self.to_keycodes_localization(tap, tap_type))
        if not self._to:
            raise Exception(f"Must map 'to' key for: {self.usr_map.from_keys}")

        if not self.conditions.get("conditions"):
            self.conditions = None

    def from_keycode_localization(self, from_map: str):
        k_list = self.keystruct_list(from_map, "from")
        simple = len(k_list) == 1
        return k_list.pop() if simple else {"simultaneous": k_list}

    def to_keycodes_localization(self, to_map: str, to_key_type: str):
        outputs = self.keystruct_list(to_map, to_key_type) if to_map else None
        return {to_key_type: outputs}

    def keystruct_list(self, key_map: str, direction: str):
        translated_key = MapTranslator(key_map)
        key_list = []

        for k in translated_key.keys:
            key = {k.key_type: k.key_code}

            if dict_value := dict_eval(k.key_code):
                key = {k.key_type: dict_value}
            elif layer := self.to_layer_check(k, direction):
                key = layer

            if modifiers := k.modifiers:
                key.update(self.local_mods(modifiers, direction, key_map))
            key_list.append(key)
        return key_list

    def local_mods(self, mods: dict, direction: str, key_map) -> dict:
        if direction == "from":
            return {"modifiers": mods}
        if mods.get("optional"):
            invalidToModType(self.usr_map)
        return {"modifiers": mods.get("mandatory")}

    def to_layer_check(self, key: namedtuple, direction: str):
        if key.key_type != "layer":
            return False
        layer_name = f"{key.key_code}_layer"

        def layer_toggle(value):
            return {"set_variable": condition_dict(layer_name, value)}

        if direction == "to_if_alone":
            # Toggle layer on. Toggle off needs to be created later by copying
            # this object and changing its on value to off
            self.layer_toggle = True
            self.conditions["conditions"].append(condition_dict(layer_name, 0))
        else:
            self._to.update(
                {"to_after_key_up": [layer_toggle(0)]}
            )

        return layer_toggle(1)

    def mapping(self):
        mapping_dict = {}
        if self.desc:
            mapping_dict.update(self.desc)
        if self.conditions:
            mapping_dict.update(self.conditions)
        mapping_dict.update(self._from)
        mapping_dict.update(self._to)
        return mapping_dict


class Karamlizer:

    def __init__(self, filename: str):
        self.yaml_data = self.load_karml(filename)
        self.karamlized_keys = {"rules": self.karamlize(self.yaml_data)}

    def load_karml(self, from_file):
        with open(from_file) as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data

    def karamlize(self, yaml_data: dict):
        karamlized_keys = []

        for layer_name, layer_maps in yaml_data.items():
            manipulators = []
            for key, to in layer_maps.items():
                user_map = UserMapping(key, to)
                karamlized_key = KaramlizedKey(user_map, layer_name)
                manipulators.append(karamlized_key.mapping())
                if karamlized_key.layer_toggle:
                    layer_off = toggle_layer_off(karamlized_key)
                    manipulators.append(layer_off.mapping())

            layer = {"description": f"{layer_name} layer",
                     "manipulators": manipulators}
            karamlized_keys.append(layer)

        return karamlized_keys

    def write_json(self, to_file: str):
        with open(to_file, "w") as f:
            f.write(dumps(self.karamlized_keys, indent=4))


def main():
    from_file = "karaml-spec.yaml"
    to_file = "karaml.json"

    karamlizer = Karamlizer(from_file)
    karamlizer.write_json(to_file)


if __name__ == "__main__":
    main()
