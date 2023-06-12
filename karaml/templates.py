"""
Defines some commonly used templates for Karabiner-Elements complex rules.

Users can also create their own template shell scripts that accept arguments.

For example, the app() template is a shell script that accepts a single
argument, the name of an application. The script then opens the application
with the open command.

The user can add a template to the templates map in the YAML file.
A template should have the format:

```
templates:
  template_name: some shell script --m %s --m %s
```

Where the %s is a placeholder for the argument(s) passed to the template.

When karaml reads the user config, it uses a regex check to determine if a map
that is in a template format is a valid template. If it is, it then checks that
the number of arguments passed to the template matches the number of %s
placeholders in the template string.

Currently, templates are strictly wrappers around shell scripts. In the future,
I would like to add support for templates for Karabiner-Elements complex
rules, giving the user more direct control over their complex rule creation.
"""

from dataclasses import dataclass
from re import search
from karaml.helpers import (
    validate_sticky_mod_value, validate_sticky_modifier, validate_var_value,
    validate_shnotify_dict, validate_mouse_pos_args,
    check_and_validate_str_as_dict,
)


@dataclass
class ShellCommandTemplate:
    """
    A class representing a user-defined shell command template.

    Attributes:
        name: The name of the template.
        template: The template string.
        args: The list of arguments for the template.
    """
    name: str
    shell_cmd_template: str

    def __post_init__(self) -> None:
        self.arg_count = self.get_num_args()

    def get_num_args(self) -> int:
        """
        Searches the template string for the number of %s placeholders.
        Returns the number of %s placeholders.
        """
        return self.shell_cmd_template.count("%s")

    def __repr__(self) -> str:
        return f"UserTemplate({self.name}, {self.shell_cmd_template}"

    def __str__(self) -> str:
        return f"UserTemplate({self.name}, {self.shell_cmd_template}"


@dataclass
class TemplateInstance:
    """
    A class representing an instance of a user-defined template.
    Reads values from a UserTemplate class, adds the user arguments as an
    attribute, and adds a method to generate the shell script, replacing
    the %s placeholders with the user arguments.
    """
    template: ShellCommandTemplate
    args: list[str]

    def __post_init__(self) -> None:

        self.shell_script = self.generate_shell_script()

    def generate_shell_script(self) -> str:
        """
        Generates the shell script by replacing the %s placeholders with the
        user arguments.
        Checks that the number of arguments passed to the template matches
        the number of %s placeholders in the template string.
        Returns the shell script.
        """
        template_name = self.template.name
        args = self.args
        arg_count = self.template.arg_count
        args_len = len(args)
        if args_len == arg_count:
            return self.template.shell_cmd_template % tuple(args)
        raise ValueError(
            f"Template {template_name} requires {arg_count} arguments, "
            f"but {args_len} were passed."
        )


# Default templates
TEMPLATES = [
    "app",
    "input",
    "mouse",
    "mousePos",
    "notify",
    "notifyOff",
    "open",
    "sfunc",
    "shell",
    "shnotify",
    "sticky",
    "var",
]

USER_TEMPLATES = {}


def update_user_templates(d: dict) -> None:
    """
    Checks the top-level key "templates" for a dict of user-defined
    templates. Each template key should have a value of a string
    representing a valid shell script.

    This function calls functions that update the TEMPLATES dict with the
    user-defined templates.

    The "templates" key is popped from the imported YAML dict after updating
    the TEMPLATES dict.

    Returns None.
    """
    templates = d.get("templates")
    if not templates:
        return

    for template, template_def in templates.items():
        template_pattern = search(r"^(\w+)\(.*\)$", template_def)
        if not (template_pattern and template_pattern.group(1)):
            # TODO: raise error
            pass
        TEMPLATES.append(template)
        USER_TEMPLATES[template] = ShellCommandTemplate(template, template_def)

    d.pop("templates")


def translate_template(event: str, cmd: str) -> tuple:
    """
    Takes strings represnting a template name and its args as arguments
    and returns a tuple with the event and command strings to create the
    appropriate KeyStruct object for the template.

    e.g. the user mapping 'shell(open .)' is returned as

    ('shell_command', 'open .')

    Which is then used to create the KeyStruct object

    KeyStruct('shell_command', 'open .', None)
    """
    # We don't actually check if the command/argument for 'open()' or
    # 'shell()' are valid links, commands, etc.) & trust the user

    # TODO: add valiation for select_input_source, mouse_key, soft_func,
    # etc. For now, it's the user's responsibility

    if template_instance := get_user_template_instance(event, cmd):
        return template_instance

    match event:
        # NOTE: need to update TEMPLATES if adding new events here
        case "app":
            return "shell_command", f"open -a '{cmd}'.app"
        case "input":
            return "select_input_source", input_source(cmd)
        case "mouse":
            return "mouse_key", mouse_key(cmd)
        case "mousePos":
            return "software_function", \
                {"set_mouse_cursor_position": mouse_pos(cmd)}
        case "notify":
            return "set_notification_message", notification(cmd)
        case "notifyOff":
            return "set_notification_message", notification_off(cmd)
        case "open":
            return "shell_command", f"open {cmd}"
        case "shell":
            return "shell_command", cmd
        case "shnotify":
            return "shell_command", shnotify(cmd)
        case "softFunc":
            return "software_function", cmd
        case "sticky":
            return "sticky_modifier", sticky_mod(cmd)
        case "var":
            return "set_variable", set_variable(cmd)
    return event, cmd


def get_user_template_instance(event: str, cmd: str) -> tuple[str, str] | None:
    """
    Returns a tuple with the event and command strings that will be used to
    create a KeyStruct for a user template instance.
    """

    if event not in USER_TEMPLATES:
        return

    template = USER_TEMPLATES[event]
    template_instance_args = [arg.strip() for arg in cmd.split(",")]
    instance = TemplateInstance(template, template_instance_args)
    return "shell_command", instance.shell_script


def input_source(regex_or_dict: str) -> dict:
    """
    Returns a dictionary for the select_input_source event.
    If the user mapping is a dictionary, tranform the string into a dictionary,
    return the dictionary and trust that the user passed a valid dictionary for
    this event.
    If the user mapping is a string, e.g. 'English', return a dictionary with
    the key 'language' and the value of the string, e.g.
    {'language': 'English'}. The former is appropriate for complex mappings,
    e.g. where a distinction between polytonic and monotonic Greek is needed,
    the latter for simple switching between languages.
    """

    if regex_dict := check_and_validate_str_as_dict(regex_or_dict):
        return regex_dict
    return {"language": regex_or_dict.strip()}


def mouse_key(mouse_key_funcs: str) -> dict:
    """
    Returns a dictionary for the mouse_key event.
    If the user mapping is a dictionary, tranform the string into a dictionary,
    return the dictionary and trust that the user passed a valid dictionary for
    this event.
    If the user mapping is a string, e.g. 'x, 200', return a dictionary with
    the key 'x' and the value of the string, e.g. {'x': 200}.
    """

    if mouse_key_dict := check_and_validate_str_as_dict(mouse_key_funcs):
        return mouse_key_dict

    key, value = mouse_key_funcs.split(",")
    return {key.strip(): float(value.strip())}


def mouse_pos(mouse_pos_args: str) -> dict:
    """
    Takes the arguments for the mousePos() template and returns a dictionary
    for the software_function event for set_mouse_cursor_position.

    The template is `mousePos(x, y, screen)` where `x` and `y` are integers and
    `screen` is an optional integer. The function returns a dictionary with
    the keys `x`, `y`, and `screen` if the screen is specified.

    Example:
    mouse_pos(200, 300, 1) --> {'x': 200, 'y': 300, 'screen': 1}
    """

    validate_mouse_pos_args(mouse_pos_args)
    formatted_args = [int(arg.strip()) for arg in mouse_pos_args.split(",")]
    x, y, *screen = formatted_args

    mouse_pos_dict = {"x": x, "y": y}
    if screen:
        mouse_pos_dict["screen"] = int(screen[0])
    return mouse_pos_dict


def notification(id_and_message: str) -> dict:
    """
    Takes the arguments for the notify() template and returns a dictionary for
    the Karabiner-Elements set_notification_message event.

    The id_and_message argument is a string with the format 'id, message' or
    'id' where id is a string and message is a string or 'null'. The function
    returns a dictionary with the keys 'id' and 'text' where 'text' is an empty
    string if the message is 'null' or the message string if it is not.

    If the message is 'null', the notification will be turned off. This matches
    the behavior of the Karabiner-Elements set_notification_message event.

    Alternatively, the `notifyOff` template, which triggers the
    `notificaion_off` function, can also turn the message off.
    """
    notification_dict = {"id": "", "text": ""}
    params = list(map(str.strip, id_and_message.split(",")))

    if len(params) == 1 or params[1].lower() == "null":
        notification_dict["text"] = ""
        notification_dict["id"] = params[0]
    elif len(params) == 2:
        notification_dict["id"] = params[0]
        notification_dict["text"] = params[1]
    return notification_dict


def notification_off(id: str) -> dict:
    """
    Alternate syntax for turning off a notification. A user might prefer
    this to passing no msg arg or 'null' as the message arg to notify().
    """
    return {"id": id.strip(), "text": ""}


def shnotify_dict(n_dict: dict) -> str:
    """
    Takes a dictionary with the keys 'msg', 'title', 'subtitle', and 'sound'
    and returns a string for the shell_command event that will display a macOS
    notification using osascript.
    """
    validate_shnotify_dict(n_dict)
    if not n_dict.get("msg"):
        n_dict["msg"] = ""
    cmd = f"osascript -e 'display notification \"{n_dict['msg']}\""

    if n_dict.get("title"):
        cmd += f" with title \"{n_dict['title']}\""
    if n_dict.get("subtitle"):
        cmd += f" subtitle \"{n_dict['subtitle']}\""
    if n_dict.get("sound"):
        cmd += f" sound name \"{n_dict['sound']}\""

    return cmd + "'"  # appended `'` closes the osascript command


def shnotify(notification: str) -> str:
    """
    Takes the arguments for the shnotify() template and returns a string for
    the shell_command event that will display a macOS notification using
    osascript.

    The `notification` arg can be formatted either as a dict with valid keys
    for an osascript notification, or as a comma separated set of args that
    are interpreted positionally and converted to a dict.
    """

    if shnofity_dict := check_and_validate_str_as_dict(notification):
        return shnotify_dict(shnofity_dict)

    formatted_notification_dict = {
        "msg": "",
        "title": "",
        "subtitle": "",
        "sound": "",
    }

    params = list(map(str.strip, notification.split(",")))

    for i, key in enumerate(formatted_notification_dict.keys()):
        if i < len(params) and params[i].lower() != "null":
            formatted_notification_dict[key] = params[i]

    return shnotify_dict(formatted_notification_dict)


def sticky_mod(sticky_mod_values: str) -> dict:
    modifier, value = sticky_mod_values.split(",")
    validate_sticky_modifier(modifier.strip())
    validate_sticky_mod_value(value.strip())
    return {modifier.strip(): value.strip()}


def set_variable(condition_items: str) -> dict:
    # NOTE: We accept any int, but the layer system checks for 0 or 1.
    # So, we should either set a constraint here (check for 0 or 1) or
    # allow more values in the layer system, e.g. default to 1 for /nav/
    # but maybe check for value == 2 for /nav/2 ?

    name, value = map(str.strip, condition_items.split(","))
    validate_var_value(name, value)
    var_dict = {"name": name, "value": int(value)}
    return var_dict
