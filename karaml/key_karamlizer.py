from dataclasses import dataclass, field

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
    to_maps: str | list

    def __post_init__(self):
        self.items = self.map_interpreter(self.to_maps)

    def map_interpreter(self, maps: str | list
                        ) -> list[str | dict | list | None]:
        """
        Converts the usere's mapping into a consisent list of three to-event
        mappings, a list of options, and a dictionary of rule parameters. If
        the user did not specify any of these, appends None to the list.
        This assumes the user followed the correct format for the mapping,
        meaning they either only included mappings in their list as far as they
        needed (e.g. [tap, hold]) or they put a placeholder `null` in any of
        the positions they did not want to specify ([null, hold, after]).
        """
        maps: list = make_list(maps)
        [maps.append(None) for i in range(5-len(maps))]
        # tap: str, hold: str, after: str, opts: list, rule_params: dict
        self.tap, self.hold, self.after, self.opts, self.rule_params = maps
        return maps


@dataclass
class KaramlizedKey:

    usr_map: UserMapping
    layer_name: str
    hold_flavor: str
    layer_toggle: list[tuple] = field(default_factory=list)
    _to: dict[str | str] = field(default_factory=dict)

    def __post_init__(self):

        self.conditions: dict = requires_sublayer(self.layer_name)

        self._from: dict = self.update_from_attr(self.usr_map)
        self.update_to()
        self.rule_params: dict = update_params(self.usr_map)
        self.modification_type: dict = update_modification_type()

    def from_keycode_dict(self, from_map: str) -> dict:
        """
        Returns a dictionary containing a key code and modifiers for a given
        "from" key map. If the key map is a simultaneous key map, returns a
        dictionary containing a list of dictionaries for each key in the
        simultaneous key map.
        """
        from_event_list: list[dict] = self.keystruct_list(from_map, "from")

        if len(from_event_list) == 1:
            return from_event_list.pop()
        return from_simultaneous_dict(from_event_list)

    def keystruct_list(self, key_map: str, event: str) -> list[dict]:
        """
        Returns a list of dictionaries, each containing a key code and
        modifiers for a given key map and event type, and options for "to"
        events if they are present.
        """
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
        """
        Return a dictionary in a format that matches a Karabiner-Elements
        compatible JSON object.
        """
        map_attrs = [self.conditions, self._from,
                     self._to, self.modification_type, self.rule_params]
        return {k: v for d in map_attrs if d for k, v in d.items()}

    def to_keycodes_dict(self, to_map: str, to_event: str) -> dict:
        """
        Returns a dictionary containing a key code for a given "to" event in
        any of its currently implemented variations
        ("to", "to_if_alone", "to_after_key_up", "to_if_held_down").
        """
        if not to_map:
            return None
        outputs = self.keystruct_list(to_map, to_event)
        to_event = chatter_safeguard(self.usr_map.hold, outputs, to_event)
        return {to_event: outputs}

    def setup_layer_toggle(self, layer_name: str, to_event: str):
        """
        Adds a toggle-off mapping to the layer_toggle queue for any layer-on
        events added to this mapping. Only applies to events that matche the
        automated format (e.g. `/layer_name/`, but not `var(layer_name, 1)`).
        Adds a condition to the mapping to check that the layer is off before
        the mapping is triggered.
        """
        self.layer_toggle.append((layer_name, to_event))
        self.conditions["conditions"].append(get_condition_dict(layer_name, 0))

    def update_conditions(self):
        """
        If no conditions have been required for this complex rule, the
        conditions attribute is set to an empty dictionary.
        """
        if not self.conditions.get("conditions"):
            self.conditions = {}

    def update_from_attr(self, usr_map: UserMapping) -> dict:
        """
        Finalizes the "_from" attribute with a dictionary containing a
        Karaibner-Elements compatible "from" event, including key codes and
        modifiers.
        """
        usr_from_maps = usr_map.from_maps
        return {"from": self.from_keycode_dict(usr_from_maps)}

    def update_to(self):
        """
        Finalizes the "_to" attribute with a dictionary containing a
        Karaibner-Elements compatible "to" event (including "to_if_alone",
        "to_after_key_up", and "to_if_held_down"), with key codes, modifiers,
        and options if they are present.
        """
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
        """
        For to events that include a layer mapping, changes the to_event
        dictionary key to "to_if_alone" if the user specified a layer mapping
        that would chatter over a "when-held" layer toggle.
        Also adds a layer-off event to the mapping if the user specified a
        layer mapping in a "when-held" position.
        """
        if key.key_type != "layer":
            return {}

        layer_name = f"{key.key_code}_layer"
        no_hold: bool = to_event == "to" and not self.usr_map.hold

        if to_if_alone := (to_event == "to_if_alone") or no_hold:
            self.setup_layer_toggle(layer_name, to_event)

            # If this is a when-tapped layer toggle, move any "to" event
            # mapping to "to_if_held_down" to prevent chatter
            if self._to.get("to") and to_if_alone:
                self._to["to_if_held_down"] = self._to.pop("to")
            return get_layer_toggle_dict(layer_name, 1)

        # If the user specified a layer mapping in a hold position, add a
        # corresponding layer-off event on release
        set_layer_off_on_release(layer_name, self._to)

        return get_layer_toggle_dict(layer_name, 1)


def get_chatty_key_type(key: dict) -> str:
    """
    Checks the list of chatty key types to see if any of those types are in the
    key dict, and returns the first one found.
    """
    for key_type in CHATTY:
        if key.get(key_type):
            return key_type
    return ""


def chatter_safeguard(hold_map: str, key_list: list, to_event: str) -> str:
    # TODO: It might have been better to check the opposite, i.e. if the
    # key is a modifier or a layer, then it's 'silent'.
    """
    Checks if a to event is considered "chatty", i.e. if it sends a key press
    on a to event that would have unintended consequences during a hold event.
    The need to handle this is a side effect of karml's design decision to
    prefer a "to" event for enabling layers when held for speed purposes (i.e.
    so we don't have to wait for a to_if_held_down threshold and reserve that
    parameter for when we want to explicitly set a threshold, which we
    presumably don't want to do for layers). See README for more on this topic.

    Returns "to_if_held_down" if the to event is chatty, otherwise returns "to"
    """
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
    """
    Returns a dict of simultaneous from-key codes and modifiers.
    of multi-key from-mappings concatenated with "+" in the config.
    """

    # FIX: This should be in tests
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


def get_condition_dict(layer_name: str, value: int) -> dict[str, dict | int]:
    """
    Returns a dict that corresponds to a Karabiner-Elements condition dict.
    This condition must be true for the "from" event to be triggered.
    """
    condition = {"name": layer_name, "type": "variable_if", "value": value}
    validate_condition_dict(condition)
    return condition


def event_value(k: KeyStruct) -> dict:
    """
    Returns a dict that corresponds to a Karabiner-Elements event, such as
    "from", "to", "to_if_alone", "to_if_held_down", etc.
    """
    if dict_value := dict_eval(k.key_code):
        return {k.key_type: dict_value}
    return {k.key_type: k.key_code}


def get_layer_toggle_dict(layer_name: str, value: int) -> dict[str, dict]:
    """
    Returns a dict that corresponds to a Karabiner-Elements set_variable dict.
    This dict will set the value of the layer to 1 or 0, which will be used
    to activate/deactivate the layer.
    """
    return {"set_variable": {"name": layer_name, "value": value}}


def local_mods(mods: dict, event: str, usr_map: UserMapping) -> dict:
    """
    Returns a dict that corresponds to a Karabiner-Elements modifiers dict.
    The user's mappings should be interpreted by this point as either
    "mandatory" or "optional" modifiers, so here we just need to check if
    1) the user has specified any modifiers, and 2) if this is a "to" event,
    then the modifiers should be "mandatory" (i.e. no parens), and then return
    a dictionary in the Karabiner-Elements format.
    """
    if not mods:
        return {}
    if event == "from":
        return {"modifiers": mods}
    # The user should not expect "to" event modifiers to be "optional", so they
    # should not map them as such in their config. All those mappings should
    # match the "mandatory" modifier style, which have no parens.
    if mods.get("optional"):
        invalidToModType(usr_map)
    return {"modifiers": mods.get("mandatory")}


def requires_sublayer(layer_name: str) -> dict[str, list[dict]]:
    """
    Returns a dict of conditions that correspond to the layer that needs to be
    active (i.e. that "layer_name" is true/false) for the mapping to be active.
    """
    conditions = {"conditions": []}
    # Get the list of layers if the current layer is a multi-layer
    # (e.g. "/layer1/+/layer2"), or add the single layer to a list.
    layers: list[str] = get_multi_keys(layer_name) or [layer_name]
    for layer in layers:
        # Confirm that the layer format is valid with regex
        found_layer = validate_layer(layer)
        # The base layer does not require any conditions - it is always active,
        # but its keys may be overridden by other layers.
        if found_layer == "base":
            return conditions
        layer_condition: dict = get_condition_dict(f"{found_layer}_layer", 1)
        conditions["conditions"].append(layer_condition)
    return conditions


def set_layer_off_on_release(layer_name: str, to_dict: dict):
    """
    Adds a "to_after_key_up" event to the "to" dict that will turn off the
    layer when the key is released. This function is called for mappings when
    a user specifies a layer-on toggle in a when-held position.
    """
    hold_toggle_off = get_layer_toggle_dict(layer_name, 0)
    if not to_dict.get("to_after_key_up"):
        to_dict.update({"to_after_key_up": [hold_toggle_off]})
    else:
        to_dict["to_after_key_up"].append(hold_toggle_off)


def get_to_opts(opts: list) -> dict:
    """
    Returns a dict with the Karabiner-Elements "to" options, such as "lazy",
    "hold_down_milliseconds", etc.
    """
    if not opts:
        return {}
    to_opts = {}
    for opt in opts:
        to_opts.update(to_opt_dict(opt))
    return to_opts


def to_opt_dict(opt: str | int) -> dict[str, int | bool]:
    """
    Returns a dict with a single key-value pair that corresponds to a
    Karabiner-Elements "to" option: "lazy", "hold_down_milliseconds",
    or "simultaneous_threshold_milliseconds".
    """
    if not opt:
        return {}
    if isinstance(opt, int):
        return {"hold_down_milliseconds": int(opt)}
    _opt, flag = validate_to_opts(opt), flag_check(opt)
    # flag may be 'False' and we want to log that
    if _opt and flag is not None:
        return {_opt: flag}
    return {}


def update_params(usr_map: UserMapping) -> dict:
    """
    Returns a dict that corresponds to a Karabiner-Elements "parameters" dict
    after translating any aliases by the user (e.g. "m" for
    "mouse_motion_to_scroll.speed") and validating the parameters.
    """
    params = usr_map.rule_params
    return translate_params(params) if params else None


def update_modification_type() -> dict:
    """
    Returns a dict that corresponds to a Karabiner-Elements "type" k/v pair
    used to update a complex modification dict.
    """
    # TODO: implement other types (mouse_motion_to_scroll)
    return {"type": "basic"}
