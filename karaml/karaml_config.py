from copy import deepcopy
from dataclasses import dataclass
import yaml

from karaml.helpers import translate_params
from karaml.key_karamlizer import KaramlizedKey, UserMapping


@dataclass
class KaramlConfig:
    from_file: str
    hold_flavor: str

    def __post_init__(self):
        self.yaml_data = self.load_karml_config(self.from_file)
        self.profile_name = self.get_profile_name(self.yaml_data)
        self.title = self.get_title(self.yaml_data)
        self.params = self.get_params(self.yaml_data)
        self.json = self.get_json(self.yaml_data)
        self.rules = self.gen_rules(self.yaml_data)
        self.insert_json()

    def gen_rules(self, yaml_data: dict) -> list:
        karamlized_keys = []

        for layer_name, layer_maps in yaml_data.items():
            manipulators = self.gen_manipulators(layer_maps, layer_name)
            layer = {"description": f"{layer_name} layer",
                     "manipulators": manipulators}
            karamlized_keys.append(layer)

        karamlized_keys.reverse()
        return karamlized_keys

    def gen_manipulators(self, layer_maps, layer_name):
        manipulators = []
        for from_keys, to_keys in layer_maps.items():
            user_map = UserMapping(from_keys, to_keys)
            key_tuple = KaramlizedKey(user_map, layer_name, self.hold_flavor)
            manipulators.append(key_tuple.mapping())
            manipulators = self.insert_toggle_off(key_tuple, manipulators)

        return manipulators

    def get_json(self, d: dict):
        json = d.pop("json") if d.get("json") else None
        return json

    def get_params(self, d: dict) -> dict:
        params = d.pop("parameters") if d.get("parameters") else None
        return translate_params(params) if params else None

    def get_profile_name(self, d: dict):
        profile_name = d.pop("profile_name") if d.get("profile_name") else None
        return profile_name

    def get_title(self, d: dict):
        title = d.pop("title") if d.get("title") else None
        return title if title else "Karaml Rules"

    def insert_json(self):
        if not self.json:
            return
        self.rules.append({
            "description": "/Karaml JSON/",
            "manipulators": self.json
        })

    def insert_toggle_off(self, karamlized_key, manipulators: list) -> list:
        layer_name = karamlized_key.layer_toggle
        if not layer_name:
            return manipulators
        layer_off = self.toggle_layer_off(karamlized_key, layer_name)
        manipulators.append(layer_off.mapping())
        print(manipulators)
        return manipulators

    def load_karml_config(self, from_file):
        with open(from_file) as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data

    def toggle_layer_off(self, karamlized_key, layer_name):
        layer_off = deepcopy(karamlized_key)
        layer_off._to["to_if_alone"][0]["set_variable"]["value"] = 0
        for condition in layer_off.conditions["conditions"]:
            if condition["name"] == layer_name:
                condition["value"] = 1

        return layer_off
