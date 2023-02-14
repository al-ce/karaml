from dataclasses import dataclass
from typing import Union
import yaml
from helpers import (make_list, get_modded_key, get_layer)

from key_codes import MODIFIERS, KEY_CODES_REF_LIST


@dataclass
class UserMapping:

    from_key: str
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
@dataclass
class MapTranslator:

    map: str

    def __post_init__(self):
        self.modifiers = []
        self.keys = make_list(self.parse_map(self.map))

    def parse_map(self, usr_key):

        if modified_key := get_modded_key(self.map):
            self.mod_translator(modified_key.modifier)
            usr_key = modified_key.key

        elif layer := get_layer(self.map):
            return "layer", layer

        return self.key_code_translator(usr_key)

    def multi_key_parser(self, user_input):

        if simul_keys := get_multi_keys(user_input):
            keys = [self.key_code_translator(k.strip()) for k in simul_keys]
            return keys

    def resolve_alias(self, usr_key: str, key_type: str, ref_list):
        if key_type != "alias":
            return
        alias = ref_list[usr_key]
        self.modifiers.append(alias.modifier) if alias.modifier else None
        return "key_code", alias.key_code

    def key_code_translator(self, usr_key):

        if simul_keys := self.multi_key_parser(usr_key):
            return simul_keys

        for kcr in KEY_CODES_REF_LIST:
            key_type, ref = kcr.key_type, kcr.ref
            if usr_key not in ref:
                continue
            if alias := self.resolve_alias(usr_key, key_type, ref):
                return alias
            key_code = ref[usr_key] if isinstance(kcr, dict) else usr_key
            return key_type, key_code

        raise Exception(exceptionWriter("key code", self.map, usr_key))

    def mod_translator(self, usr_mods):
        for mod in usr_mods:
            if mod_query := MODIFIERS.get(mod):
                self.modifiers.append(mod_query)
                continue
            raise Exception(exceptionWriter("modifier", self.map, mod))
