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

    def queue_translations(self, parsed_key: str):
        if multi_keys := get_multi_keys(parsed_key):
            return [self.key_code_translator(k.strip()) for k in multi_keys]
        else:
            return [self.key_code_translator(parsed_key)]

    def key_code_translator(self, usr_key: str):

        if layer := is_layer(self.map):
            return KeyStruct("layer", layer, None)

        for ref_list in KEY_CODE_REF_LISTS:
            parsed_key, modifiers = self.parse_modifiers(usr_key)
            key_type, ref = ref_list.key_type, ref_list.ref

            if parsed_key not in ref:
                continue

            if dealiased_key := self.resolve_alias(parsed_key, key_type, ref):
                return KeyStruct("key_code", dealiased_key, modifiers)
            return KeyStruct(key_type, parsed_key, modifiers)

        raise Exception(invalidKey("key code", self.map, usr_key))

    def resolve_alias(self, usr_key: str, key_type: str, aliases_dict: dict):
        if key_type != "alias":
            return
        alias = aliases_dict[usr_key]
        self.get_modifiers(alias.modifier) if alias.modifier else None
        return alias.key_code


@dataclass
class KeyConverter:

    mapping: UserMapping

    def __post_init__(self):

        # self.desc = {}
        # self.insert_desc()
        from_map = self.mapping.from_keys
        self._from = {"from": self.from_keycode_localization(from_map)}

        self._to = {}
        tap_key_name = "to"
        if hold := self.mapping.hold:
            self._to.update(self.to_keycodes_localization(hold, "to"))
            tap_key_name = "to_if_alone"

        if tap := self.mapping.tap:
            self._to.update(self.to_keycodes_localization(tap, tap_key_name))

        if not self._to:
            raise Exception(f"Must map 'to' key for: {self.mapping.from_keys}")
    def parse_keystruct(self, key_dict):
        converted_key_dict = MapTranslator(key_dict)
    def local_mods(self, mods: dict, direction: str, key_map) -> dict:
        if direction == "from":
            return {"modifiers": mods}
        if mods.get("optional"):
            invalidToModType(self.mapping)
        return {"modifiers": mods.get("mandatory")}

    def parse_keystruct(self, key_map: str, direction: str):
        translated_key = MapTranslator(key_map)
        key_list = []

        for k in translated_key.keys:
            key = {k.key_type: k.key_code}
            if modifiers := k.modifiers:
                key.update(self.local_mods(modifiers, direction, key_map))
            key_list.append(key)
        return key_list

    def from_keycode_localization(self, from_map: str):
        k_list = self.parse_keystruct(from_map, "from")
        simple = len(k_list) == 1
        return k_list.pop() if simple else {"simultaneous": k_list}

    def to_keycodes_localization(self, to_map: str, to_key_type: str):
        outputs = self.parse_keystruct(to_map, "to") if to_map else None
        return {to_key_type: outputs}
            self._from["from"]["modifiers"] = modifiers

    def _update_to_keys(self, to_map, to_key_name):
        converted = MapTranslator(to_map)
        outputs = self.to_localization(converted)
        self._to.update({to_key_name: outputs})
        modifiers = self.to_modifiers_localization(converted)
        if modifiers:
            self._to.update({"modifiers": modifiers})

    def to_localization(self, to_map):
        if not to_map:
            return
        return {k.key_type: k.key_code for k in to_map.keys}

    def to_modifiers_localization(self, to_map):
        modifiers = filter_list([k.modifiers for k in to_map.keys])
        if modifiers:
            return modifiers
        return to_list
