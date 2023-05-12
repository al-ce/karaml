# Assuming a list of key codes as determined from this GH comment from the repo
# https://github.com/pqrs-org/Karabiner-Elements/issues/925#issuecomment-942284498


from string import ascii_uppercase
from collections import namedtuple

Alias = namedtuple("Alias", ["key_code", "modifiers"])


alias_shift_mod = ["shift"]
ALIASES = {

    # Unicode chars without side indicator default to left side
    "⌘": Alias("left_command", None),
    "‹⌘": Alias("left_command", None),
    "⌘›": Alias("right_command", None),
    "⌥": Alias("left_option", None),
    "‹⌥": Alias("left_option", None),
    "⌥›": Alias("right_option", None),
    "⌃": Alias("left_control", None),
    "‹⌃": Alias("left_control", None),
    "⌃›": Alias("right_control", None),
    "⇧": Alias("left_shift", None),
    "‹⇧": Alias("left_shift", None),
    "⇧›": Alias("right_shift", None),

    "lcmd": Alias("left_command", None),
    "rcmd": Alias("right_command", None),
    "lalt": Alias("left_option", None),
    "ralt": Alias("right_option", None),
    "lctrl": Alias("left_control", None),
    "rctrl": Alias("right_control", None),
    "lshft": Alias("left_shift", None),
    "rshft": Alias("right_shift", None),

    "hyper": Alias("right_shift", [
        "right_command",
        "right_control",
        "right_option",
    ]),
    "☆": Alias("fn", ["shift", "command", "control", "option"]),
    "ultra": Alias("right_shift", [
        "right_command",
        "right_control",
        "right_option",
        "fn",
    ]),
    "super": Alias("right_shift", ["right_option", "right_control"]),
    "enter": Alias("return_or_enter", None),
    "cr": Alias("return_or_enter", None),
    "CR": Alias("return_or_enter", None),
    "esc": Alias("escape", None),
    "ESC": Alias("escape", None),
    "⎋": Alias("escape", None),
    "⇥": Alias("tab", None),
    "backspace": Alias("delete_or_backspace", None),
    "bs": Alias("delete_or_backspace", None),
    "BS": Alias("delete_or_backspace", None),
    "delete": Alias("delete_forward", None),
    "DEL": Alias("delete_forward", None),
    "del": Alias("delete_forward", None),
    "space": Alias("spacebar", None),
    "SPC": Alias("spacebar", None),
    "spc": Alias("spacebar", None),
    " ": Alias("spacebar", None),
    "-": Alias("hyphen", None),
    "underscore": Alias("hyphen", alias_shift_mod),
    "_": Alias("hyphen", alias_shift_mod),
    "=": Alias("equal_sign", None),
    "plus": Alias("equal_sign", alias_shift_mod),
    "(": Alias("9", alias_shift_mod),
    ")": Alias("0", alias_shift_mod),
    "[": Alias("open_bracket", None),
    "{": Alias("open_bracket", alias_shift_mod),
    "]": Alias("close_bracket", None),
    "}": Alias("close_bracket", alias_shift_mod),
    "\\": Alias("backslash", None),
    "|": Alias("backslash", alias_shift_mod),
    ";": Alias("semicolon", None),
    ":": Alias("semicolon", alias_shift_mod),
    "'": Alias("quote", None),
    '"': Alias("quote", alias_shift_mod),
    "grave": Alias("grave_accent_and_tilde", None),
    "`": Alias("grave_accent_and_tilde", None),
    "~": Alias("grave_accent_and_tilde", alias_shift_mod),
    ",": Alias("comma", None),
    "<": Alias("comma", alias_shift_mod),
    ".": Alias("period", None),
    ">": Alias("period", alias_shift_mod),
    "/": Alias("slash", None),
    "?": Alias("slash", alias_shift_mod),
    "!": Alias("1", alias_shift_mod),
    "@": Alias("2", alias_shift_mod),
    "#": Alias("3", alias_shift_mod),
    "$": Alias("4", alias_shift_mod),
    "%": Alias("5", alias_shift_mod),
    "^": Alias("6", alias_shift_mod),
    "&": Alias("7", alias_shift_mod),
    "*": Alias("8", alias_shift_mod),
    "up": Alias("up_arrow", None),
    "down": Alias("down_arrow", None),
    "left": Alias("left_arrow", None),
    "right": Alias("right_arrow", None),
    "↑": Alias("up_arrow", None),
    "↓": Alias("down_arrow", None),
    "←": Alias("left_arrow", None),
    "→": Alias("right_arrow", None),
    "pgup": Alias("page_up", None),
    "pgdn": Alias("page_down", None),
    "kp-": Alias("keypad_hyphen", None),
    "kpminus": Alias("keypad_hyphen", None),
    "kpplus": Alias("keypad_plus", None),
    "kp*": Alias("keypad_asterisk", None),
    "kp/": Alias("keypad_slash", None),
    "kp=": Alias("keypad_equal_sign", None),
    "kp.": Alias("keypad_period", None),
    "kp,": Alias("keypad_comma", None),
    "kpenter": Alias("keypad_enter", None),
    "kp1": Alias("keypad_1", None),
    "kp2": Alias("keypad_2", None),
    "kp3": Alias("keypad_3", None),
    "kp4": Alias("keypad_4", None),
    "kp5": Alias("keypad_5", None),
    "kp6": Alias("keypad_6", None),
    "kp7": Alias("keypad_7", None),
    "kp8": Alias("keypad_8", None),
    "kp9": Alias("keypad_9", None),
    "kp0": Alias("keypad_0", None),
    "kpnum": Alias("keypad_num_lock", None),
}

for letter in ascii_uppercase:
    ALIASES[letter] = Alias(letter.lower(), alias_shift_mod)

MODIFIERS = {
    "m": "left_command",
    "o": "left_option",
    "c": "left_control",
    "s": "left_shift",
    "M": "right_command",
    "O": "right_option",
    "C": "right_control",
    "S": "right_shift",
    "f": "fn",
    "F": "fn",
    "l": "caps_lock",
    "L": "caps_lock",
    "x": "any",
    "X": "any",


    # HACK: g and a are sensible aliases but r and h are stretches
    "G": "command",
    "R": "control",
    "A": "option",
    "H": "shift",
    "g": "command",
    "r": "control",
    "a": "option",
    "h": "shift",
}


MODIFIER_ALIASES = {
    "⌘": "g",
    "⌥": "a",
    "⌃": "r",
    "⇧": "h",
    "‹⌘": "m",
    "⌘›": "M",
    "‹⌥": "o",
    "⌥›": "O",
    "‹⌃": "c",
    "⌃›": "C",
    "‹⇧": "s",
    "⇧›": "S",
    "☆": "garh",
}

KEY_CODE = [
    "caps_lock",
    "return_or_enter",
    "escape",
    "delete_or_backspace",
    "delete_forward",
    "tab",
    "spacebar",
    "hyphen",
    "equal_sign",
    "open_bracket",
    "close_bracket",
    "backslash",
    "non_us_pound",
    "semicolon",
    "quote",
    "grave_accent_and_tilde",
    "comma",
    "period",
    "slash",
    "non_us_backslash",
    "up_arrow",
    "down_arrow",
    "left_arrow",
    "right_arrow",
    "page_up",
    "page_down",
    "home",
    "end",
    "a",
    "b",
    "c",
    "d",
    "e",
    "f",
    "g",
    "h",
    "i",
    "j",
    "k",
    "l",
    "m",
    "n",
    "o",
    "p",
    "q",
    "r",
    "s",
    "t",
    "u",
    "v",
    "w",
    "x",
    "y",
    "z",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "0",
    "f1",
    "f2",
    "f3",
    "f4",
    "f5",
    "f6",
    "f7",
    "f8",
    "f9",
    "f10",
    "f11",
    "f12",
    "f13",
    "f14",
    "f15",
    "f16",
    "f17",
    "f18",
    "f19",
    "f20",
    "f21",
    "f22",
    "f23",
    "f24",
    "keypad_num_lock",
    "keypad_slash",
    "keypad_asterisk",
    "keypad_hyphen",
    "keypad_plus",
    "keypad_enter",
    "keypad_1",
    "keypad_2",
    "keypad_3",
    "keypad_4",
    "keypad_5",
    "keypad_6",
    "keypad_7",
    "keypad_8",
    "keypad_9",
    "keypad_0",
    "keypad_period",
    "keypad_equal_sign",
    "keypad_comma",
    "vk_none",
    "print_screen",
    "scroll_lock",
    "pause",
    "insert",
    "application",
    "help",
    "power",
    "execute",
    "menu",
    "select",
    "stop",
    "again",
    "undo",
    "cut",
    "copy",
    "paste",
    "find",
    "international1",
    "international2",
    "international3",
    "international4",
    "international5",
    "international6",
    "international7",
    "international8",
    "international9",
    "lang1",
    "lang2",
    "lang3",
    "lang4",
    "lang5",
    "lang6",
    "lang7",
    "lang8",
    "lang9",
    "japanese_eisuu",
    "japanese_kana",
    "japanese_pc_nfer",
    "japanese_pc_xfer",
    "japanese_pc_katakana",
    "left_control",
    "left_shift",
    "left_option",
    "left_command",
    "right_control",
    "right_shift",
    "right_option",
    "right_command",
    "fn",
    "keypad_equal_sign_as400",
    "locking_caps_lock",
    "locking_num_lock",
    "locking_scroll_lock",
    "alternate_erase",
    "sys_req_or_attention",
    "cancel",
    "clear",
    "prior",
    "return",
    "separator",
    "out",
    "oper",
    "clear_or_again",
    "cr_sel_or_props",
    "ex_sel",
    "left_alt",
    "left_gui",
    "right_alt",
    "right_gui",
    "vk_consumer_brightness_down",
    "vk_consumer_brightness_up",
    "vk_mission_control",
    "vk_launchpad",
    "vk_dashboard",
    "vk_consumer_illumination_down",
    "vk_consumer_illumination_up",
    "vk_consumer_previous",
    "vk_consumer_play",
    "vk_consumer_next",
    "volume_down",
    "volume_up",
    "display_brightness_decrement",
    "display_brightness_increment",
    "rewind",
    "play_or_pause",
    "fastforward",
    "mute",
    "volume_decrement",
    "volume_increment",
    "apple_display_brightness_decrement",
    "apple_display_brightness_increment",
    "dashboard",
    "launchpad",
    "mission_control",
    "fn",
    "apple_top_case_display_brightness_decrement",
    "apple_top_case_display_brightness_increment",
    "illumination_decrement",
    "illumination_increment",
]

CONSUMER_KEY_CODE = [
    "display_brightness_decrement",
    "display_brightness_increment",
    "dictation",
    "rewind",
    "play_or_pause",
    "fast_forward",
    "mute",
    "volume_decrement",
    "volume_increment",
    "menu",
    "al_terminal_lock_or_screensaver",
    "eject",
    "scan_previous_track",
    "scan_next_track",
    "fastforward",
]

POINTING_BUTTON = [
    "button1",
    "button2",
    "button3",
    "button4",
    "button5",
    "button6",
    "button7",
    "button8",
    "button9",
    "button10",
    "button11",
    "button12",
    "button13",
    "button14",
    "button15",
    "button16",
    "button17",
    "button18",
    "button19",
    "button20",
    "button21",
    "button22",
    "button23",
    "button24",
    "button25",
    "button26",
    "button27",
    "button28",
    "button29",
    "button30",
    "button31",
    "button32",
]


KeyCodesRef = namedtuple("KeyCodesRef", ["key_type", "ref"])

KEY_CODE_REF_LISTS = [
    KeyCodesRef("alias", ALIASES),
    KeyCodesRef("key_code", KEY_CODE),
    KeyCodesRef("consumer_key_code", CONSUMER_KEY_CODE),
    KeyCodesRef("pointing_button", POINTING_BUTTON),
]

# NOTE: As of KE 14.12.0, "shift", "command", etc. are not valid sticky mods
STICKY_MODS = [
    "left_control",
    "left_shift",
    "left_option",
    "left_command",
    "right_control",
    "right_shift",
    "right_option",
    "right_command",
    "fn",
]

CHATTY = [
    "key_code",
    "consumer_key_code",
    "pointing_button",
    "shell_command",
    # NOTE: I think notifications shouldn't be considered chatty,
    # but open to reconsidering
    # "set_notification_message",
    "mouse_key",
    "select_input_source",
    "sticky_modifier",
    "software_function"
]
