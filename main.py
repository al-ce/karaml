from collections import namedtuple
from dataclasses import dataclass
from json import dumps
from typing import Union
import yaml
from helpers import (
    invalidKey, invalidToModType, make_list, is_modded_key, is_layer,
    get_multi_keys, modifier_lookup, parse_chars_in_parens
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
        self.get_modifiers(alias.modifier) if alias.modifier else None
        return alias.key_code


@dataclass
class KaramlizedKey:

    mapping: UserMapping

    def __post_init__(self):

        self.conditions = {}
        self.layer_toggle = False

        desc = self.mapping.desc
        self.desc = {"description": desc} if desc else None

        from_map = self.mapping.from_keys
        self._from = {"from": self.from_keycode_localization(from_map)}

        self._to = {}
        tap_type = "to"
        if hold := self.mapping.hold:
            self._to.update(self.to_keycodes_localization(hold, "to"))
            tap_type = "to_if_alone"
        if tap := self.mapping.tap:
            self._to.update(self.to_keycodes_localization(tap, tap_type))
        if not self._to:
            raise Exception(f"Must map 'to' key for: {self.mapping.from_keys}")

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
            elif layer := self.layer_check(k, direction):
                key = layer

            if modifiers := k.modifiers:
                key.update(self.local_mods(modifiers, direction, key_map))
            key_list.append(key)
        return key_list

    def local_mods(self, mods: dict, direction: str, key_map) -> dict:
        if direction == "from":
            return {"modifiers": mods}
        if mods.get("optional"):
            invalidToModType(self.mapping)
        return {"modifiers": mods.get("mandatory")}

    def layer_check(self, key: namedtuple, direction: str):
        if key.key_type != "layer":
            return False
        layer_name = f"{key.key_code}_layer"

        def layer_toggle(value):
            return {"set_variable": {"name": layer_name, "value": value}}

        if direction == "to_if_alone":
            # Toggle layer on. Toggle off needs to be created later by copying
            # this object and changing its on/off value
            self.layer_toggle = True
            self.conditions = {"conditions": [layer_toggle(0)]}
        else:
            # To: layer on
            # To after key up: layer off
            self._to.update(
                {"to_after_key_up": [layer_toggle(0)]}
            )

        return layer_toggle(1)

    def to_modifiers_localization(self, to_map):
        modifiers = filter_list([k.modifiers for k in to_map.keys])
        if modifiers:
            return modifiers
        return to_list
