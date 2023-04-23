from copy import deepcopy
from dataclasses import dataclass
from typing import Union
import yaml

from karaml.user_aliases import update_user_aliases
from karaml.helpers import (
    translate_params,
    UniqueKeyLoader,
)
from karaml.exceptions import invalidFrontmostAppCondition
from karaml.key_karamlizer import KaramlizedKey, UserMapping
from karaml.templates import update_user_templates


def extract_keys(mapping_node):
    print("Value:")
    if not isinstance(mapping_node, yaml.nodes.MappingNode):
        print("    ", mapping_node.value)
        return mapping_node
    for key_node, _ in mapping_node.value:
        key = key_node.value
        print("    ", key)


@dataclass
class KaramlConfig:
    from_file: str
    hold_flavor: str

    def __post_init__(self):
        self.yaml_data: dict = self.load_karaml_config(self.from_file)
        self.profile_name: str = self.get_profile_name(self.yaml_data)
        self.title: str = self.get_ruleset_title(self.yaml_data)
        self.params: dict = self.get_params(self.yaml_data)
        self.json_rules_list: list = self.get_json_rules_list(self.yaml_data)
        update_user_templates(self.yaml_data)
        update_user_aliases(self.yaml_data)
        self.layers: list = self.gen_layers(self.yaml_data)

        self.config_stats()

    def load_karaml_config(self, from_file: str) -> dict:
        """
        Loads a karaml config file and returns a dict of the yaml data imported
        by the PyYAML library.
        """
        with open(from_file) as f:
            yaml_data: dict = yaml.load(f, Loader=UniqueKeyLoader)
        return yaml_data

    def config_stats(self) -> dict:
        """
        Prints a summary of the loaded layers and rules in the config file
        to stdout. Layers are determined by the number of top-level keys
        in the config that match the pattern /layer_name/ (e.g. /layer1/).
        All other top-level keys are ignored.
        """

        rule_count = 0
        for layer_name, layer_maps in self.yaml_data.items():
            # Account for multiple layer conditions (e.g. /layer1/ + /layer2/)
            if layer_name.startswith("/") and layer_name.endswith("/"):
                rule_count += len(layer_maps)
        total_layers = len(self.layers)
        print(f"Loaded {rule_count} rules in {len(self.layers)} layers "
              f"from {self.from_file}\n")
        return {"total_rules": rule_count, "total_layers": total_layers}

    def get_profile_name(self, d: dict) -> str:
        """
        Returns the profile name specified in the config file, or an empty
        string if no profile name is specified.
        """
        return d.pop("profile_name") if d.get("profile_name") else ""

    def get_ruleset_title(self, d: dict) -> str:
        """
        Returns the ruleset title specified in the config file, or a default
        title "Karaml Rules" if no title is specified.
        """
        return d.pop("title") if d.get("title") else "Karaml Rules"

    def get_params(self, d: dict) -> dict:
        """
        Returns the complex modification parameters specified in the config if
        there are any, including:

        basic.to_if_alone_timeout_milliseconds: 100,
        basic.to_if_held_down_threshold_milliseconds: 101,
        basic.to_delayed_action_delay_milliseconds: 150,
        basic.simultaneous_threshold_milliseconds: 75,
        mouse_motion_to_scroll.speed: 100,

        As of version 1.0 of Karaml, to_delayed_action_delay_milliseconds is
        not actually supported since the to_delayed_action key is not
        implemented.
        """

        params = d.pop("parameters") if d.get("parameters") else {}
        return translate_params(params) if params else {}

    def get_json_rules_list(self, d: dict) -> list:
        """
        Returns a list of JSON-formatted rules from the YAML config file by
        checking the top-level key "json" for a list of rules. JSON rules allow
        a user to specify any rule that is not fully supported by Karaml's YAML
        syntax by using any valid Karabiner-Elements rule (such as
        to_delayed_action for doube-tap modifiers).
        """
        return d.pop("json") if d.get("json") else []

    def gen_layers(self, yaml_data: dict) -> list:
        """
        Returns a list of layers, where each layer is a dict with a description
        containing the layer's name, and a list of manipulators. Each layer is
        equivalent to a complex modification ruleset in Karabiner-Elements.
        """
        layers_list = []

        for layer_name, layer_maps in yaml_data.items():
            manipulators: list = self.get_manipulators(layer_name, layer_maps)
            layer = {"description": f"{layer_name} layer",
                     "manipulators": manipulators}
            layers_list.append(layer)

        layers_list: list = self.insert_json(layers_list)
        # Reverse the list so that later mappings override earlier ones in
        # 'higher' layers
        layers_list.reverse()
        return layers_list

    def get_manipulators(self, layer_name: str, layer_maps: dict) -> list:
        """
        Returns a list of manipulators for a given layer. Each item in the list
        is an object (KaramlizedKey) equivalent to a Karabiner-Elements rule.
        The KaramlizedKey objects are intrepreted from the layer_maps dict,
        which is a dict of key mappings read into memory from the YAML Karaml
        config file by the PyYAML library.
        """
        manipulators = []
        for from_keys, rhs in layer_maps.items():
            gkk_args = [from_keys, layer_name, self.hold_flavor]
            # If the rhs is a single complex modification
            if type(rhs) in [list, str]:
                karamlized_key = get_karamlized_key(*gkk_args, rhs)
                manipulators.append(karamlized_key.make_mapping_dict())
                manipulators = self.insert_toggle_off(
                    karamlized_key, manipulators)

            # If this map is a dict of frontmost app based conditions, which
            # may contain multiple complex modifications
            elif type(rhs) == dict:
                # Append a modification for each condition
                for frontmost_app_key, to_keys in rhs.items():
                    karamlized_key = get_karamlized_key(*gkk_args, to_keys)
                    frontmost_app_dict = get_app_conditions_dict(
                        frontmost_app_key, rhs)
                    karamlized_key.conditions["conditions"].append(
                        frontmost_app_dict)

                    manipulators.append(karamlized_key.make_mapping_dict())
                    manipulators = self.insert_toggle_off(
                        karamlized_key, manipulators)

        return manipulators

    def insert_json(self, layers_list: list) -> list:
        """
        Inserts a JSON layer at the end of the layers list if the user gave any
        JSON-formatted rules in the YAML config file. Returns the layers list.
        """
        if not self.json_rules_list:
            return layers_list
        layers_list.append({
            "description": "/JSON/ layer",
            "manipulators": self.json_rules_list
        })
        return layers_list

    def insert_toggle_off(self, karamlized_key: KaramlizedKey,
                          manipulators: list) -> list:
        """
        Inserts a corresponding layer-off rule for a layer-on rule if the user
        specified a layer toggle in the YAML config file into the manipulators
        list. Returns the manipulators list.

        Layer-off rules are auto-generated so that the user does not have to
        map a different key to turn off a layer if they mapped a layer-on key
        with the `/layer_name/` syntax in the YAML config file. This syntax
        is intended for automating the layer-off rule, so the user does not
        have to map a different key to turn off a layer. To turn layers on or
        off manually, the user should use the `var(layer_name, value)` syntax.
        """
        # BUG: If a user maps something to the same key as the auto-generated
        # layer-off rule, the layer-off rule will be overridden, so the user
        # could potentially get stuck in a layer if they have no other way to
        # turn it off. Perhaps a user might be ok with this, but they should
        # be warned.

        toggle_info: list = karamlized_key.layer_toggle
        if not toggle_info:
            return manipulators
        layer_off: KaramlizedKey = self.toggle_layer_off(karamlized_key,
                                                         toggle_info)
        manipulators.append(layer_off.make_mapping_dict())
        return manipulators

    def toggle_layer_off(self, karamlized_key: KaramlizedKey,
                         toggle_info: list) -> KaramlizedKey:
        """
        Returns a KaramlizedKey object that turns off the layer turned on by
        the corresponding karamlized_key arg. The toggle_info arg is a list of
        tuples containing the layer name and the event that toggled the layer
        on.
        """
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


def get_app_conditions_dict(app_conditions: str, rhs: dict) -> dict:
    """
    Returns a dict containing the frontmost application conditions for a
    complex modification, matching the Karabiner-Elements format.
    The app_conditions arg is a str type key in the rhs dict that should begin
    with "if" or "unless" and be followed by regex patterns for the frontmost
    application's bundle identifier. The rhs arg is the dict that contains the
    app_conditions arg.
    """
    conditional, *regex = app_conditions.split(" ")
    if conditional not in ["if", "unless"]:
        invalidFrontmostAppCondition(conditional, rhs)
    return {
        "type": f"frontmost_application_{conditional}",
        "bundle_identifiers": regex
    }


def get_karamlized_key(from_keys: str, layer_name: str, hold_flavor: str,
                       rhs: Union[str, list]) -> KaramlizedKey:
    """
    Returns an object that contains the information needed to generate a
    Karabiner-Elements rule. The user_map converts the user's mapping into a
    consistent format of a from_keys string and a to_keys list.
    Each KaramlizedKey object is equivalent to a Karabiner-Elements complex
    modification rule.
    """
    user_map = UserMapping(from_keys, rhs)
    return KaramlizedKey(user_map, layer_name, hold_flavor)
