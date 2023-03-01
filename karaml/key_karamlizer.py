from dataclasses import dataclass, field
from typing import Dict, List, Union

from karaml.helpers import (
    dict_eval, flag_check, is_layer, get_multi_keys, make_list,
    validate_to_opts, translate_params, validate_condition_dict, validate_layer
)
from karaml.key_codes import (
    CHATTY, MODIFIERS, KEY_CODE_REF_LISTS, PSEUDO_FUNCS
)
from karaml.exceptions import (
    invalidToModType, missingToMap
)
from karaml.map_translator import TranslatedMap, KeyStruct


@dataclass
class UserMapping:

    from_maps: str
    to_maps: Union[str, list]

    def __post_init__(self):
        self.items = self.map_interpreter(self.to_maps)

    def map_interpreter(self, maps):
        maps = make_list(maps)
        [maps.append(None) for i in range(5-len(maps))]
        self.tap, self.hold, self.after, self.opts, self.rule_params = maps
        return maps


@dataclass
class KaramlizedKey:

    usr_map: UserMapping
    layer_name: str
    hold_flavor: str
    layer_toggle: List[tuple] = field(default_factory=list)
    _to: Dict[str, str] = field(default_factory=dict)

    def __post_init__(self):

        self.conditions: dict = requires_sublayer(self.layer_name)
        # self.layer_toggle = []

        self._from: dict = self.update_from_attr(self.usr_map)
        # self._to = {}
        self.update_to()
        self.rule_params: dict = update_params(self.usr_map)
        self.modification_type: dict = update_modification_type()

    def from_keycode_dict(self, from_map: str) -> dict:
        from_event_list = self.keystruct_list(from_map, "from")

        if len(from_event_list) == 1:
            return from_event_list.pop()
        return from_simultaneous_dict(from_event_list)

    def keystruct_list(self, key_map: str, event: str) -> list[dict]:
        translated_key = TranslatedMap(key_map)
        key_list = []

        for k in translated_key.keys:
            layer: dict = self.to_layer_check(k, event)
            key: dict = layer if layer else event_value(k)
            mod_list = local_mods(k.modifiers, event, self.usr_map)
            key.update(mod_list)
            opts = get_to_opts(self.usr_map.opts) if event == "to" else {}
            key.update(opts)
            key_list.append(key)

        return key_list

    def make_mapping_dict(self) -> dict:
        map_attrs = [self.conditions, self._from,
                     self._to, self.modification_type, self.rule_params]
        return {k: v for d in map_attrs if d for k, v in d.items()}

    def to_keycodes_dict(self, to_map: str, to_event: str) -> dict:
        if not to_map:
            return None
        outputs = self.keystruct_list(to_map, to_event)
        to_event = chatter_safeguard(self.usr_map, outputs, to_event)
        return {to_event: outputs}

    def setup_layer_toggle(self, layer_name: str, to_event: str):
        self.layer_toggle.append((layer_name, to_event))
        self.conditions["conditions"].append(get_condition_dict(layer_name, 0))

    def update_conditions(self):
        if not self.conditions.get("conditions"):
            self.conditions = None

    def update_from_attr(self, usr_map: UserMapping) -> dict:
        usr_from_maps = usr_map.from_maps
        return {"from": self.from_keycode_dict(usr_from_maps)}

    def update_to(self):

        tap_type = "to"
        if after := self.usr_map.after:
            self._to.update(self.to_keycodes_dict(after, "to_after_key_up"))
        if hold := self.usr_map.hold:
            hold_type = self.hold_flavor
            self._to.update(self.to_keycodes_dict(hold, hold_type))
            tap_type = "to_if_alone"
        if tap := self.usr_map.tap:
            self._to.update(self.to_keycodes_dict(tap, tap_type))
        if not self._to:
            missingToMap(self.usr_map.from_maps)

    def to_layer_check(self, key: KeyStruct, to_event: str) -> dict:
        if key.key_type != "layer":
            return False

        layer_name = f"{key.key_code}_layer"
        no_hold = to_event == "to" and not self.usr_map.hold

        if to_if_alone := (to_event == "to_if_alone") or no_hold:
            self.setup_layer_toggle(layer_name, to_event)

            # If this is a when-tapped layer toggle, move any "to" event
            # mapping to "to_if_held_down" to prevent chatter
            if self._to.get("to") and to_if_alone:
                self._to["to_if_held_down"] = self._to.pop("to")
            return get_layer_toggle_dict(layer_name, 1)

        set_layer_off_on_release(layer_name, self._to)

        return get_layer_toggle_dict(layer_name, 1)


def get_chatty_key_type(key: dict) -> str:
    for key_type in CHATTY:
        if key.get(key_type):
            return key_type


def chatter_safeguard(usr_map: UserMapping, key_list: list, to_event: str) -> str:
    hold_map = usr_map.hold
    if to_event != "to" or not hold_map:
        return to_event

    # Pseudo funcs/special events are chatty except for notify
    for pf in PSEUDO_FUNCS:
        if pf == "notify":
            continue
        if pf in hold_map:
            return "to_if_held_down"

    for key in key_list:
        key_type = get_chatty_key_type(key)
        key_code = key.get(key_type) if key_type else None
        if not key_code:
            continue
        if key_code not in MODIFIERS.values() and not is_layer(str(key_code)):
            return "to_if_held_down"
    return "to"


def from_simultaneous_dict(from_event_list: list[dict]) -> dict:

    if len(from_event_list) < 2:
        raise Exception("Single length 'from' events shouldn't make it here!")

    key_codes, merged_mods = [], {"mandatory": [], "optional": []}
    for k in from_event_list:
        # key_codes.append(k["key_code"])
        for kc_type, ref_list in KEY_CODE_REF_LISTS:
            if kc := k.get(kc_type):
                key_codes.append({kc_type: kc})
                break
        mods = k.get("modifiers")
        if not mods:
            continue
        if mandatory := mods.get("mandatory"):
            merged_mods["mandatory"] += mandatory
        if optional := mods.get("optional"):
            merged_mods["optional"] += optional

    fs_dict = {"simultaneous": [kc_entry for kc_entry in key_codes]}
    merged_mods = {k: v for k, v in merged_mods.items() if v}
    if merged_mods:
        fs_dict["modifiers"] = merged_mods
    return fs_dict


def get_condition_dict(layer_name: str, value: int) -> dict:
    condition = {"name": layer_name, "type": "variable_if", "value": value}
    validate_condition_dict(condition)
    return condition


def event_value(k: KeyStruct) -> dict:
    if dict_value := dict_eval(k.key_code):
        return {k.key_type: dict_value}
    return {k.key_type: k.key_code}


def get_layer_toggle_dict(layer_name: str, value: int) -> dict:
    return {"set_variable": {"name": layer_name, "value": value}}


def local_mods(mods: dict, event: str, usr_map: UserMapping) -> dict:
    if not mods:
        return {}
    if event == "from":
        return {"modifiers": mods}
    if mods.get("optional"):
        invalidToModType(usr_map)
    return {"modifiers": mods.get("mandatory")}


def requires_sublayer(layer_name: str) -> dict:
    conditions = {"conditions": []}
    layers = get_multi_keys(layer_name) or [layer_name]
    for layer in layers:
        found_layer = validate_layer(layer)
        if found_layer == "base":
            return conditions
        layer_condition = get_condition_dict(f"{found_layer}_layer", 1)
        conditions["conditions"].append(layer_condition)
    return conditions


def set_layer_off_on_release(layer_name: str, to_dict: dict):
    hold_toggle_off = get_layer_toggle_dict(layer_name, 0)
    if not to_dict.get("to_after_key_up"):
        to_dict.update({"to_after_key_up": [hold_toggle_off]})
    else:
        to_dict["to_after_key_up"].append(hold_toggle_off)
    return to_dict


def get_to_opts(opts: list) -> dict:
    if not opts:
        return {}
    to_opts = {}
    for opt in opts:
        to_opts.update(to_opt_dict(opt))
    return to_opts


def to_opt_dict(opt: list) -> dict:
    if not opt:
        return {}
    if isinstance(opt, int):
        return {"hold_down_milliseconds": int(opt)}
    _opt, flag = validate_to_opts(opt), flag_check(opt)
    # flag may be 'False' and we want to log that
    if _opt and flag is not None:
        return {_opt: flag}
    return {}


def update_params(usr_map: UserMapping):
    params = usr_map.rule_params
    return translate_params(params) if params else None


def update_modification_type():
    # TODO: implement other types (mouse_motion_to_scroll)
    return {"type": "basic"}
