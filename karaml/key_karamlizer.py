from collections import namedtuple
from dataclasses import dataclass
from re import search
from typing import Union

from karaml.helpers import (
    dict_eval, flag_check, get_multi_keys, make_list, validate_opt,
    translate_params, validate_layer
)
from karaml.exceptions import invalidToModType
from karaml.key_codes import MODIFIERS
from karaml.map_translator import TranslatedMap


def condition_dict(layer_name: str, value: int) -> dict:
    return {"name": layer_name, "type": "variable_if", "value": value}


def event_value(k: namedtuple):
    if dict_value := dict_eval(k.key_code):
        return {k.key_type: dict_value}
    return {k.key_type: k.key_code}


def layer_toggle(layer_name, value):
    return {"set_variable": {"name": layer_name, "value": value}}


def local_mods(mods: dict, direction: str, usr_map) -> dict:
    if not mods:
        return {}
    if direction == "from":
        return {"modifiers": mods}
    if mods.get("optional"):
        invalidToModType(usr_map)
    return {"modifiers": mods.get("mandatory")}


def requires_sublayer(layer_name: str) -> str:
    conditions = {"conditions": []}
    layers = get_multi_keys(layer_name) or [layer_name]
    for layer in layers:
        found_layer = validate_layer(layer)
        if found_layer == "base":
            return conditions
        layer_condition = condition_dict(f"{found_layer}_layer", 1)
        conditions["conditions"].append(layer_condition)
    return conditions


def get_to_opts(opts: list) -> dict:
    if not opts:
        return {}
    to_opts = {}
    for opt in opts:
        to_opts.update(to_opt_dict(opt))
    return to_opts


def to_opt_dict(opt):
    if not opt:
        return {}
    if isinstance(opt, int):
        return {"hold_down_milliseconds": int(opt)}
    _opt, flag = validate_opt(opt), flag_check(opt)
    if _opt and flag:
        return {_opt: flag}
    return {}


@dataclass
class UserMapping:

    from_keys: str
    maps: Union[str, list]

    def __post_init__(self):
        self.map_interpreter(self.maps)

    def items(self):
        return self.tap, self.hold, self.after, self.opts, self.rule_params

    def map_interpreter(self, maps):
        maps = make_list(maps)
        [maps.append(None) for i in range(5-len(maps))]
        self.tap, self.hold, self.after, self.opts, self.rule_params = maps


@dataclass
class KaramlizedKey:

    usr_map: UserMapping
    layer_name: str
    hold_flavor: str

    def __post_init__(self):

        self.conditions = requires_sublayer(self.layer_name)
        self.layer_toggle = []

        self.update_from()
        self.update_to()
        self.update_conditions()
        self.update_params()
        self.update_type()

    def from_keycode_dict(self, from_map: str):
        k_list = self.keystruct_list(from_map, "from")
        simple = len(k_list) == 1
        return k_list.pop() if simple else {"simultaneous": k_list}

    def keystruct_list(self, key_map: str, to_event: str):
        translated_key = TranslatedMap(key_map)
        key_list = []

        for k in translated_key.keys:
            layer = self.to_layer_check(k, to_event)
            key = layer if layer else event_value(k)
            mod_list = local_mods(k.modifiers, to_event, self.usr_map)
            key.update(mod_list)
            opts = get_to_opts(self.usr_map.opts) if to_event == "to" else {}
            key.update(opts)
            key_list.append(key)

        return key_list

    def mapping(self):
        map_attrs = [self.conditions, self._from,
                     self._to, self._type, self.rule_params]
        return {k: v for d in map_attrs if d for k, v in d.items()}

    def to_keycodes_dict(self, to_map: str, to_event: str):
        outputs = self.keystruct_list(to_map, to_event) if to_map else None
        return {to_event: outputs}

    def to_layer_check(self, key: namedtuple, to_event: str):
        if key.key_type != "layer":
            return False
        layer_name = f"{key.key_code}_layer"

        no_hold = to_event == "to" and not self.usr_map.hold
        if to_if_alone := (to_event == "to_if_alone") or no_hold:

            # Toggle off needs to be created later by deep-copying this object,
            # changing its on value to off, and adding it to the mapping.
            # This automation overrides any to_after_key_up set by the user
            self.setup_layer_toggle(layer_name, to_event)

            # Override "to" hold flavor in case of layer toggle to prevent
            # "non-harmless" key sends
            if self._to.get("to") and to_if_alone:
                self._to["to_if_held_down"] = self._to.pop("to")

        else:
            self._to.update(
                {"to_after_key_up": [layer_toggle(layer_name, 0)]}
            )

        return layer_toggle(layer_name, 1)

    def setup_layer_toggle(self, layer_name, to_event):
        self.layer_toggle.append((layer_name, to_event))
        self.conditions["conditions"].append(condition_dict(layer_name, 0))

    def update_conditions(self):
        if not self.conditions.get("conditions"):
            self.conditions = None

    def update_from(self):
        from_map = self.usr_map.from_keys
        self._from = {"from": self.from_keycode_dict(from_map)}

    def update_params(self):
        params = self.usr_map.rule_params
        self.rule_params = translate_params(params) if params else None

    def update_to(self):
        self._to = {}

        tap_type = "to"
        # to_after_key_up must execute first so it is overridden by the
        # automated layer-toggle-off if a layer is activated when a key is held
        if after := self.usr_map.after:
            self._to.update(self.to_keycodes_dict(after, "to_after_key_up"))
        if hold := self.usr_map.hold:
            hold_type = self.hold_flavor

            self._to.update(self.to_keycodes_dict(hold, hold_type))
            tap_type = "to_if_alone"
        if tap := self.usr_map.tap:
            self._to.update(self.to_keycodes_dict(tap, tap_type))
        if not self._to:
            raise Exception(f"Must map 'to' key for: {self.usr_map.from_keys}")

    def update_type(self):
        # TODO: implement other types (mouse_motion_to_scroll)
        self._type = {"type": "basic"}