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
        self.yaml_data = self.load_karaml_config(self.from_file)
        self.profile_name = self.get_profile_name(self.yaml_data)
        self.title = self.get_title(self.yaml_data)
        self.params = self.get_params(self.yaml_data)
        self.json = self.get_json_rules_list(self.yaml_data)
        self.layers = self.gen_layers(self.yaml_data)

    def load_karaml_config(self, from_file):
        with open(from_file) as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data

    def config_stats(self):
        rule_count = 0
        for layer_name, layer_maps in self.yaml_data.items():
            # account for multiple layer conditions (e.g. /layer1/ + /layer2/)
            if layer_name.startswith("/") and layer_name.endswith("/"):
                rule_count += len(layer_maps)
        total_layers = len(self.layers)
        print(f"Loaded {rule_count} rules in {len(self.layers)} layers "
              "from {self.from_file}\n")
        return {"total_rules": rule_count, "total_layers": total_layers}

    def get_profile_name(self, d: dict):
        profile_name = d.pop("profile_name") if d.get("profile_name") else None
        return profile_name

    def get_title(self, d: dict):
        title = d.pop("title") if d.get("title") else None
        return title if title else "Karaml Rules"

    def get_params(self, d: dict) -> dict:
        params = d.pop("parameters") if d.get("parameters") else None
        return translate_params(params) if params else None

    def get_json_rules_list(self, d: dict):
        json = d.pop("json") if d.get("json") else None
        return json

    def gen_layers(self, yaml_data: dict) -> list:
        layers_list = []

        for layer_name, layer_maps in yaml_data.items():
            manipulators = self.gen_manipulators(layer_name, layer_maps)
            layer = {"description": f"{layer_name} layer",
                     "manipulators": manipulators}
            layers_list.append(layer)

        layers_list = self.insert_json(layers_list)
        # Reverse the list so that later mappings override earlier ones in
        # 'higher' layers
        layers_list.reverse()
        return layers_list

    def gen_manipulators(self, layer_name, layer_maps):
        manipulators = []
        for from_keys, to_keys in layer_maps.items():
            user_map = UserMapping(from_keys, to_keys)
            key_tuple = KaramlizedKey(user_map, layer_name, self.hold_flavor)
            manipulators.append(key_tuple.make_mapping_dict())
            manipulators = self.insert_toggle_off(key_tuple, manipulators)

        return manipulators

    def insert_json(self, layers_list: list) -> list:
        if not self.json:
            return layers_list
        layers_list.append({
            "description": "/JSON/ layer",
            "manipulators": self.json
        })
        return layers_list

    def insert_toggle_off(self, karamlized_key, manipulators: list) -> list:
        toggle_info: list = karamlized_key.layer_toggle
        if not toggle_info:
            return manipulators
        layer_off = self.toggle_layer_off(karamlized_key, toggle_info)
        manipulators.append(layer_off.make_mapping_dict())
        return manipulators

    def toggle_layer_off(self, karamlized_key, toggle_info: list):
        layer_off = deepcopy(karamlized_key)
        for layer_name, event in toggle_info:
            for condition in layer_off.conditions["conditions"]:
                if condition["name"] == layer_name:
                    condition["value"] = 1
            for to_event in layer_off._to[event]:
                if not to_event.get("set_variable"):
                    continue
                if to_event["set_variable"]["name"] == layer_name:
                    to_event["set_variable"]["value"] = 0

        return layer_off
