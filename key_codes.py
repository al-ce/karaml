# Assuming a list of key codes as determined from this GH comment from the repo
# https://github.com/pqrs-org/Karabiner-Elements/issues/925#issuecomment-942284498


from string import ascii_uppercase
from collections import namedtuple

Alias = namedtuple("Alias", ["key_code", "modifier"])


modifier = "left_shift"
ALIASES = {
    "enter": Alias("return_or_enter", None),
    "backspace": Alias("delete_or_backspace", None),
    "delete": Alias("delete_forward", None),
    "-": Alias("hyphen", None),
    "_": Alias("hyphen", modifier),
    "=": Alias("equal_sign", modifier),
    "(": Alias("9", modifier),
    ")": Alias("0", modifier),
    "[": Alias("open_bracket", None),
    "{": Alias("open_bracket", modifier),
    "]": Alias("close_bracket", None),
    "}": Alias("close_bracket", modifier),
    "\\": Alias("backslash", None),
    "|": Alias("backslash", modifier),
    ";": Alias("semicolon", None),
    ":": Alias("semicolon", modifier),
    "'": Alias("quote", None),
    '"': Alias("quote", modifier),
    "`": Alias("grave_accent_and_tilde", None),
    "~": Alias("grave_accent_and_tilde", modifier),
    ",": Alias("comma", None),
    "<": Alias("comma", modifier),
    ".": Alias("period", None),
    ">": Alias("period", modifier),
    "/": Alias("slash", None),
    "?": Alias("slash", modifier),
    "up": Alias("up_arrow", None),
    "down": Alias("down_arrow", None),
    "left": Alias("left_arrow", None),
    "right": Alias("right_arrow", None),
    "pgup": Alias("page_up", None),
    "pgdn": Alias("page_down", None),
    "home": Alias("home", None),
    "end": Alias("end", None),
}

for letter in ascii_uppercase:
    ALIASES[letter] = [letter.lower(), True]

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
    "l": "caps_lock",
    "x": "any",
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
