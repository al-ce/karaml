"""
Allows the user to create template shell scripts that accept arguments.

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
        if len(self.args) != self.template.arg_count:
            raise ValueError(
                f"Template {self.template.name} requires {self.template.arg_count} arguments, "
                f"but {len(self.args)} were passed."
            )
        return self.template.shell_cmd_template % tuple(self.args)


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
    if not d.get("templates"):
        return
    templates = d.get("templates")

    for template, template_def in templates.items():
        template_pattern = search(r"^(\w+)\(.*\)$", template_def)
        if not (template_pattern and template_pattern.group(1)):
            # TODO: raise error
            pass
        TEMPLATES.append(template)
        USER_TEMPLATES[template] = ShellCommandTemplate(template, template_def)

    d.pop("templates")
