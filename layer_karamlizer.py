from json import dumps
import yaml

from helpers import toggle_layer_off
from key_karamlizer import KaramlizedKey, UserMapping


class LayerKaramlizer:

    def __init__(self, filename: str):
        self.yaml_data = self.load_karml_config(filename)
        self.karamlized_layers = {"rules": self.karamlize(self.yaml_data)}

    def gen_manipulators(self, layer_maps, layer_name):
        manipulators = []
        for from_keys, to_keys in layer_maps.items():
            user_map = UserMapping(from_keys, to_keys)
            karamlized_key = KaramlizedKey(user_map, layer_name)
            manipulators.append(karamlized_key.mapping())
            manipulators = self.insert_toggle_off(karamlized_key, manipulators)

        return manipulators

    def insert_toggle_off(self, karamlized_key, manipulators: list) -> list:
        if not karamlized_key.layer_toggle:
            return manipulators
        layer_off = toggle_layer_off(karamlized_key)
        manipulators.append(layer_off.mapping())
        return manipulators

    def karamlize(self, yaml_data: dict):
        karamlized_keys = []

        for layer_name, layer_maps in yaml_data.items():
            manipulators = self.gen_manipulators(layer_maps, layer_name)
            layer = {"description": f"{layer_name} layer",
                     "manipulators": manipulators}
            karamlized_keys.append(layer)

        karamlized_keys.reverse()
        return karamlized_keys

    def load_karml_config(self, from_file):
        with open(from_file) as f:
            yaml_data = yaml.safe_load(f)
        return yaml_data

    def write_json(self, to_file: str):
        with open(to_file, "w") as f:
            f.write(dumps(self.karamlized_layers, indent=4))
