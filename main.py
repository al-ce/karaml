from collections import namedtuple
from dataclasses import dataclass
from typing import Union
import yaml
from helpers import (
    invalidKey, make_list, is_modded_key,
    is_layer, get_multi_keys, validate_modifier_rules
)

from key_codes import MODIFIERS, KEY_CODE_REF_LISTS

KeyStruct = namedtuple("KeyStruct", ["key_type", "key_code"])


@dataclass
class UserMapping:

    from_keys: str
    maps: Union[str, list]

    def __post_init__(self):
        self.map_interpreter(self.maps)

    def map_interpreter(self, maps):
        maps = make_list(maps)
        # Set any undefined attributes to None so we avoid AttributeError
        [maps.append(None) for i in range(3-len(maps))]
        self.tap, self.hold, self.desc = maps

    def items(self):
        return self.tap, self.hold, self.desc

    def __repr__(self):
        return f"Tap: {self.tap}\nHold: {self.hold}\nDesc: {self.desc}"


@dataclass
class MapTranslator:

    map: str

    def __post_init__(self):
        self.modifiers = []
        parsed_key = self.parse_modifiers(self.map)
        translated_keys = self.queue_translations(parsed_key)
        self.keys = translated_keys

    def parse_modifiers(self, usr_key):
        if modified_key := is_modded_key(self.map):
            self.append_modifiers(modified_key.modifier)
            return modified_key.key
        return usr_key

    def append_modifiers(self, usr_mods):
        for mod in usr_mods:
            if mod_query := MODIFIERS.get(mod):
                self.modifiers.append(mod_query)
                continue
            raise Exception(invalidKey("modifier", self.map, mod))

    def queue_translations(self, parsed_key):
        if multi_keys := get_multi_keys(parsed_key):
            return [self.key_code_translator(k.strip()) for k in multi_keys]
        else:
            return [self.key_code_translator(parsed_key)]

    def key_code_translator(self, usr_key):

        if layer := is_layer(self.map):
            return KeyStruct("layer", layer)

        for ref_list in KEY_CODE_REF_LISTS:
            key_type, ref = ref_list.key_type, ref_list.ref

            if usr_key not in ref:
                continue

            if dealiased_key := self.resolve_alias(usr_key, key_type, ref):
                return KeyStruct("key_code", dealiased_key)
            return KeyStruct(key_type, usr_key)

        raise Exception(invalidKey("key code", self.map, usr_key))

    def resolve_alias(self, usr_key: str, key_type: str, aliases_list):
        if key_type != "alias":
            return
        alias = aliases_list[usr_key]
        self.modifiers.append(alias.modifier) if alias.modifier else None
        return alias.key_code

    def __repr__(self):
        # Type: {self.key_type}
        return f"""\
        Key: {self.keys}
        Modifiers:{[m for m in self.modifiers]}"""


@dataclass
class Converter:

    mapping: UserMapping

    def __post_init__(self):
        self.from_keys = {}
        from_map = MapTranslator(self.mapping.from_keys)
        self.from_keycode_localization(from_map)
        self.from_modifiers_localization(from_map)

        if tap := self.mapping.tap:
            converted_tap_map = MapTranslator(tap)
            self.to_localization(converted_tap_map)
            self.to_modifiers_localization(converted_tap_map)

        if hold := self.mapping.hold:
            # If hold, then to_localization needs to be a 'to if alone' key,
            # else just 'to'
            pass

    def from_keycode_localization(self, from_map):
        # from: is a dictionary in karabiner.config
        container = [{k.key_type: k.key_code} for k in from_map.keys]

        if len(container) == 1:
            self.from_keys.update(container[0])
        else:
            self.from_keys["simultaneous"] = [k for k in container]

    def from_modifiers_localization(self, from_map):
        # modifiers are a dict in the from dict, but a list in the to list
        user_modifiers = from_map.modifiers
        if not user_modifiers:
            return
        rule = validate_modifier_rules(self.mapping.from_keys)
        self.from_keys["modifiers"] = {rule: user_modifiers}

    def to_localization(self, to_map):
        # to: is a list in karabiner.config
        if not to_map:
            self.to_keys = None
            return
        self.to_keys = [{k.key_type: k.key_code} for k in to_map.keys]

    def to_modifiers_localization(self, to_map):
        # modifiers a list in the to list. No modifier rules to check
        user_modifiers = to_map.modifiers
        if not user_modifiers:
            return
        self.to_keys.append({"modifiers": user_modifiers})
