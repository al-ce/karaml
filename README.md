# karaml 🍮


**karaml** (**_Kara_**biner in ya**_ml_**) lets you write and maintain a virtual layers-based Karabiner-Elements configuration in YAML.

It is a yaml-based implementation of the philosophy of [mxstbr](https://github.com/mxstbr)'s Karabiner [config](https://github.com/mxstbr/karabiner) and of [yqrashawn](https://github.com/yqrashawn/)'s [Goku](https://github.com/yqrashawn/GokuRakuJoudo) tool, using Python to translate the yaml into Karabiner-compatible JSON.

Thanks to [mxstbr](https://github.com/mxstbr) and [yqrashawn](https://github.com/yqrashawn/) for the inspiration for this project.


<!--toc:start-->
- [✨ Features](#features)
- [❓ Why this project](#why-this-project)
  - [Why YAML?](#why-yaml)
- [⚡️ Quickstart](#️-quickstart)
- [⚙️  YAML Configuration](#️-yaml-configuration)
  - [Basic Mapping and Layer Structure](#basic-mapping-and-layer-structure)
  - [Enabling Layers](#enabling-layers)
  - [Modifiers](#modifiers)
  - [Key-Code Aliases](#key-code-aliases)
  - [Special Event Functions](#special-event-functions)
    - [App Launchers](#app-launchers)
    - [Open Browser Link](#open-browser-link)
    - [Shell Commands](#shell-commands)
    - [Input Sources](#input-sources)
    - [Mouse Movement](#mouse-movement)
    - [Notifications](#notifications)
    - [Sticky Modifiers](#sticky-modifiers)
    - [Software Functions](#software-functions)
    - [Variables](#variables)
  - [Global parameters](#global-parameters)
  - [Profile Name and Complex-Modification Title](#profile-name-and-complex-modification-title)
  - [JSON Extension Map](#json-extension-map)
- [🎨 About the Design](#🎨-about-the-design)
- [🔩 Requirements](#🔩-requirements)
- [📦 Installation](#📦-installation)
- [🚀 Usage](#🚀-usage)
- [CLI prompt](#cli-prompt)
  - [-k mode](#k-mode)
  - [-c mode](#c-mode)
  - [-d (debug) mode](#-d-(debug)-mode)
- [🌱 TODO](#🌱-todo)
- [🔭 Alternatives](#🔭-alternatives)
<!--toc:end-->


```yaml
/base/:
  caps_lock: [escape, /nav/] # Escape when tapped, /nav/ layer when held
  <oc-n>: /nav/              # Tap Left Opt + Left Ctrl + n to toggle /nav/
  <O-w>: <o-backspace>       # Right Opt + w to Left Opt + Backspace

  # Enter when tapped, Left Control when held, lazy flag, any optional modifiers
  <(x)-enter>:
    - enter
    - left_control
    - null                   # No event when released
    - [+lazy]

  j+k: [escape, button1]     # j+k to escape when tapped, left click when held

  # option (either side) + o/O to create new line below/above
  <a-o>: <m-right> + return
  <a-O>: up + <m-right> + return


/nav/:
  <(x)-h>: left              # vim navigation with any optional mods
  <(x)-j>: down
  <(x)-k>: up
  <(x)-l>: right
  s: [app(Safari), /sys/]    # Launch Safari on tap, /sys/ layer when held
  g: open(https://github.com)

/sys/:
  <o-m>: [mute, null, mute]  # Mute if held/key down, unmute if released/key up
  k: play_or_pause
  "}": fastforward
  u: shell(open -b com.apple.ScreenSaver.Engine) # Start Screen Saver

json:                        # JSON integration
  - {
      description: 'Right Shift to ) if tapped, Shift if held',
      from: { key_code: right_shift },
      to: { key_code: right_shift, lazy: true },
      to_if_alone: { key_code: 9, modifiers: [shift] },
      type: basic,
    }
```


## ✨ Features

- Complex modifications on a single line of yaml
- Map complex events (app launches, shell commands, etc.), enable layers (set variables), and require conditions with shorthand syntax
- Events for when a key is tapped, held, and released in a sequential array (rather than k/v pairs)
- Simple schema for requiring mandatory or optional modifiers in a pseudo-Vim style
- Aliases for symbols, shifted keys, and complex names (e.g. `grave_accent_and_tilde` → `grave`, `left_shift` + `[` → `{` )
- Accepts regular Karabiner JSON in an 'appendix' table so all cases Karaml can't or doesn't plan to handle can still be in one config
- Automatically update your `karabiner.json` or write to the complex modifications folder and import manually
- Checks and formatting hints for your `.yaml` file - karaml will try not to let you
  upload a config that won't create an actual modification, even if you wrote it in the
  equivalent Karabiner-compatible JSON


## ❓ Why this project

The `karabiner.json` file can be hard to manage and visualize as it grows, as
the JSON format requires a lot of lines, carefully managed opening and closing
quotes, brackets, and commas, and repetitive conditional logic.

**karaml** tries to simplify this by providing a more readable, maintainable,
and easy to adjust format in YAML. This means making some trade-offs in
completeness of features, but I try to come close with minimal sacrifices to
simplicity. To prevent the need for maintaining multiple configurations, **karaml** 
also supports an 'appendix' table for any Karabiner-compatible JSON that can't
be expressed in karaml.

### Why YAML?

- Easy to maintain: no mandatory quotes, but quotes can simplify escaping
  troublesome characters; minimal or no use of brackets around keys/values
- [Easy to learn](https://learnxinyminutes.com/docs/yaml/) and easy to read
- A superset of JSON which allows us to fall back to JSON if wanted/needed


## ⚡️ Quickstart
After [installing](#📦-installation), take the [sample YAML configuration](./docs/sample_configuration.yaml) and alter it, or follow the [configuration guide](/docs/config_guide.md).
See one of my configurations [here](./docs/al-ce_config.yaml).
Then follow the [usage instructions](#🚀-usage) below. 
If you're unfamiliar with YAML, take a look at this handy [guide](https://learnxinyminutes.com/docs/yaml/).

## ⚙️  YAML Configuration

### Basic Mapping and Layer Structure
All keys belong to a layer. At minimum, a map requires a `from: to` structure
and must be in a layer:

```yaml
/layer_name/:
  from_key: to_key
```

This is equivalent to:
```json
{
  "from": { "key_code": "from_key" },
  "to": { "key_code": "to_key" } "type": "basic",
  "conditions": [ { "name": "layer_name_layer", "type": "variable_if", "value": 1 } ]
}
```

In your karaml config, you need to add a `/base/` layer, but only as a matter
of convention. Maps in the `/base/` layer don't check for conditions and you
don't need to enable that layer.

To add additional events or options to your maps, put them in a yaml array or sequence.

```yaml
/layer_name/:   # All mappings below require the 'layer_name' layer enabled
  from_key(s): [when_tapped, when_held, when_released, [to_opts], {params}]
```

As shown above, you can add as many or as few items to the array as you like.

### Enabling Layers

In the 'to' part of the map, enable layers with `/layer_name/`. In the first
position, the layer will be tap-toggled by the 'from'. In the second position,
the layer will be enabled when the 'from' key is held.

```yaml
/base/:
  <oc-n>: /nav/               # enabled/disabled on tap
  caps_lock: [escape, /nav/]  # enabled when held

# The maps indented in this layer will only work when the layer is enabled
/nav/:
  h: left
  j: down
  k: up
  l: right
```


### Modifiers

Follow the format `<modifiers-primary_key>`. Join multiple modifiers with `+` 
and wrap optional modifiers in parens.

Whether the optional set in parens comes first or last doesn't matter, e.g. `<(c)os-g>` and `<os(c)-g>` are both valid. But a single set of optional modifiers in parens must be to the right or left of *all* mandatory modifiers (if there are any mandatory modifiers).

Left side modifiers are lowercase, right side modifiers are uppercase.

`<c-h>` → `left_ctrl` + `h`
`<(x)-h` → `h` (with any optional modifiers)
`<mOC(s)-h>` → `left_cmd` + `right_opt` + `right_ctrl` + `left_shift` (optional) + `h`
`<(s)mOC-h>` →   (same as above)
`<m(ocs)-h>` → `left_cmd` (mandatory) + `right_opt` `right_ctrl` + `left_shift` (optional) + `h`
`<(ocs)m-h>`   (same as above)


| key_code     | karaml | --- | key_code | karaml |
| -------------- | ------ | --- | -------------- | ------ |
| `left_control` | `c`  | --- | `right_control` | `C`  |
| `left_shift`   | `s`  | --- | `right_shift`   | `S`  |
| `left_option`  | `o`  | --- | `right_option`  | `O`  |
| `left_command` | `m`  | --- | `right_command` | `M`  |
| `control`      | `r`  | --- | `control`       | `R`  |
| `shift`        | `h`  | --- | `shift`         | `H`  |
| `option`       | `a`  | --- | `option`        | `A`  |
| `command`      | `g`  | --- | `command`       | `G`  |


### Key-Code Aliases

You can follow the explicit mapping for any key (e.g. `<s-1>` → `!`), or use
these available aliases. Be mindful in your YAML config that some characters
need to be escaped or wrapped in quotes to be recognied as strings.

<details>
<summary>Key-Code Aliases</summary>

| karaml alias | Karabiner key_code            |
| ------------ | ----------------------------- |
| enter        | return_or_enter               |
| backspace    | delete_or_backspace           |
| delete       | delete_forward                |
| space        | spacebar                      |
| -            | hyphen                        |
| underscore   | hyphen + shift                |
| \_           | hyphen + shift                |
| =            | equal_sign                    |
| (            | 9 + shift                     |
| )            | 0 + shift                     |
| [            | open_bracket                  |
| {            | open_bracket + shift          |
| ]            | close_bracket                 |
| }            | close_bracket + shift         |
| \\           | backslash                     |
| \|           | backslash + shift             |
| ;            | semicolon                     |
| :            | semicolon + shift             |
| '            | quote                         |
| "            | quote + shift                 |
| grave        | grave_accent_and_tilde        |
| `            | grave_accent_and_tilde        |
| ~            | grave_accent_and_tilde+ shift |
| ,            | comma                         |
| <            | comma + shift                 |
| .            | period                        |
| >            | period + shift                |
| /            | slash                         |
| ?            | slash + shift                 |
| up           | up_arrow                      |
| down         | down_arrow                    |
| left         | left_arrow                    |
| right        | right_arrow                   |
| pgup         | page_up                       |
| pgdn         | page_down                     |
| kp-          | keypad_hyphen                 |
| kp+          | keypad_plus                   |
| kp\*         | keypad_asterisk               |
| kp/          | keypad_slash                  |
| kp=          | keypad_equal_sign             |
| kp.          | keypad_period                 |
| kp,          | keypad_comma                  |
| kpenter      | keypad_enter                  |
| kp1          | keypad_1                      |
| kp2          | keypad_2                      |
| kp3          | keypad_3                      |
| kp4          | keypad_4                      |
| kp5          | keypad_5                      |
| kp6          | keypad_6                      |
| kp7          | keypad_7                      |
| kp8          | keypad_8                      |
| kp9          | keypad_9                      |
| kp0          | keypad_0                      |
| kpnum        | keypad_num_lock               |

</details>

### Special Event Functions

Shorthands for common-use events. Mostly wrappers around the [to.shell_command](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/shell-command/) event.

<details>

<summary>Special Event Functions</summary>

#### App Launchers

`app(app_name)`

Pass an app name (as it appears in your Applications folder) as an argument to
`app()`. I like using these in my `/nav/` layer for quick access, but you might
want these in a standalone `/apps/` layer.

#### Open Browser Link

`open(url)`

Open a url with your default browser.

#### Shell Commands

`shell(shell command)`

Pass a [shell command](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/shell-command/) as an argument to `shell()`. This is what the app() and open()
'functions' are actually doing under the hood. Please suggest other useful
shorthands of shell commands that we could add!

#### Input Sources

`input(lang_regex)`
`input({"language": "regex", "input_source_id": "regex", "input_mode_id": "regex" })`

Either pass a language regex as an argument to `input()` to select the first
available input source that matches the regex, or pass a
string representing a JSON object with all the valid Karabiner fields as specified [here](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/select-input-source/).

#### Mouse Movement

`mouse(action, speed|multiplier)`

Using the [to.mouse_key event](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/mouse-key/), you can pass a two arguments that represent a key/value pair of movement/speed,
or the speed_multiplier key and its multiplier value.
If you want to assign multiple mouse events to the mapping, you can pass a
string representing a JSON object matching the Karabiner specs, just like with
input sources.

#### Notifications

`notify(id, message)`

The id is the reference for updating the notification with the message on subsequent calls.

#### Sticky Modifiers

`sticky(modifier, toggle)`

Pass two arguments: the modifier to be held on the next keypress (must be a
valid modifier key code), and whether to toggle the modifier, turn it on, or
turn it off ('on | off | toggle')

#### Software Functions

`softFunc( {"function name": nested_dict} )`

Takes a string representing a JSON object with all the valid Karabiner fields as specified [here](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/soft-function/).

#### Variables

The `var()` function takes two arguments: a variable name and a value (0 or 1).
See the [to.set_variable documentation](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/set-variable/)

karaml intends variables to be handled as layers and automates some mappings
under the hood to streamline toggling and enabling layers, but the `var()`
function allows more granular control.

</details>

### Global parameters

Add a `parameters` map to your `.yaml` file to set global parameters for your
profile. These parameters will be applied to all mappings in the profile unless
overridden by a mapping's own parameters object.

```yaml
parameters:
  {
    "basic.to_if_alone_timeout_milliseconds": 100,
    "basic.to_if_held_down_threshold_milliseconds": 101,
    basic.to_delayed_action_delay_milliseconds: 150,
    "basic.simultaneous_threshold_milliseconds": 75,
    "mouse_motion_to_scroll.speed": 100,
  }


/base/:
  # ...
```

### Profile Name and Complex-Modification Title

Add a `profile` map to your `.yaml` file to set the profile name and a `title`
map to set the complex-modification title. Both are optional, and you can leave
them in your config even if you don't use the profile-creation or the
complex-modification writing feature. If you don't provide either, karaml will
generate default placeholders before it writes the file.

```yaml
# If a profile name is not provided, one will be generated from the
# current Unix timestamp
profile_name:
  Karaml Config


title:
  KaramlRules

```

### JSON Extension Map

Add a `json` map to the `.yaml` file to include Karabiner-compatible JSON. This
is intended for cases where karaml doesn't support a feature you need, or when
you think the JSON looks easier to read than the karaml syntax, but you still
want to use karaml for the rest of your config.

Be mindful of the slight differences in syntax between yaml and JSON.
Namely, quotes are optional unless needed for escaping characters, elements of
the `json` map are separated as sequence item (a properly indented dash `-`
followed by a space), and no commas are used to separate those items.

***WARNING!***: karaml 'inspects' your regular yaml-flavored configuration for
proper formatting - not just whether you wrote it in a syntax karaml can
intrepret, but also whether you used valid key codes, valid modifiers, etc.
karaml also formats the modification's dictionary for you so you don't have to keep
track of what level of bracket nesting you're in, whether you should have used
`[]` or `{}`, added or forgot a comma, etc. Currently, karaml doesn't support
these 'health checks' for the JSON extension map, so karaml will just append
whatever you put in there to the rule-set.

```yaml
/base/:
  # ...

/nav/:
  # ...

json:
  - {
    # No need for quotes since there are no chars that need escaping
    description: Right Control to > if tapped and control if held,
      from: { key_code: right_control },
      to: { key_code: right_control, lazy: true },
      to_if_alone: { key_code: period, modifiers: [right_control] },
      type: basic,
    }
  - {
      # Quotes needed in the description because of the comma.
      # We can also add quotes just if we want to
      "description": "Left Control to < if tapped, control if held",
      "from": { "key_code": "left_control" },
      "to": { "key_code": "left_control", "lazy": true },
      "to_if_alone": { "key_code": "comma", "modifiers": ["left_control"] },
      "type": "basic",
    }
```

## 🐍️ Python backend for handling your files

The program reads your `.yaml` config with the PyYAML module, interprets your
layers and keybindings, checking that they are all well-formed along the way,
and creates 'KaramlizedKey' objects with all the relevant attributes (from 
events, to events, options, modifiers, etc.) that are eventually converted into
Karabiner-compatible JSON.

karaml then either updates your existing `karabiner.json ` file or your
complex-modifications folder.

- If you elect to update `karabiner.json` directly:
  - karaml makes a copy of the current `karabiner.json` file and adds that copy
  to `~/.config/karabiner/automatic_backups/` as `karabiner.backup.TIMESTAMP.json`,
  every time (thirty of my ~6000 line Karabiner JSON bacskups add up to ~10MB,
  so check in every once in a while)
  - karaml then searches the `profiles` list in `karabiner.json` for a profile
    name that matches the one in your config (or generates a new one if you
    didn't specify it - add one!). If it finds a match, it will replace that
    profile with the new config generated from the `.yaml` file, otherwise it
    just appends a new profile to the list
- If you elect to add your karaml config as a ruleset to the
  complex-modifications folder:
  - If you passed the `-c` flag in the command line, karaml expects a filename
    to write to. If you're using the CLI menu, karaml will default to
    creating/overwriting `karaml_complex_mods.json`. If the file already
    exists, you'll get a confirmation prompt. karaml doesn't backup your
    complex-mods files
  - If you have a `title` map in your `.yaml` file, karaml will use that as the
    title of your complex-modification ruleset. If you don't, karaml will title
    your ruleset as `KaramlRules`

## 🎨 About the Design

Understanding a standard Karabiner configuration is useful for leveraging the
most out of karaml, but at its core karaml is designed to reduce events to
either `when_tapped` and `when_held` actions (also `when_released`, but that's
automated when layers are enabled when held).

`when_tapped` is mapped to either `to` or `to_if_alone`, and `when_held` is
mapped to either `to` or `to_if_held_down` depending on whether the map enables
a layer, a modifier, or a notification ('non-chatty' events) when held.

karaml was designed around toggling layers or enabling modifiers when a key is
held down, and letting the key have some other function when tapped. I found
that, for my typing style, a 100ms `to_if_alone_timeout_milliseconds` setting,
mapping the 'when tapped' function to `to_if_alone` and the 'when held'
functions to a 'to' dictionary (instead of 'to_if_held_down') provided
immediate switching between layers or enabling of modifier keys. This means
sending the `to` event even when `to_if_alone` is sent, but so long as the
event is 'harmless', or not 'chatty', i.e. it is a layer, a modifier, or a
notfication, and so long as we set the `lazy` opt when necessary (e.g. for my
mapping of `enter` → `control` when held), this doesn't cause any significant
side effects.

When a 'chatty' event would have side-effects, or when sending an event on
'if held down' following the relevant parameters is an explicit goal (rather
than just a way of distinguishing a tap from a hold), karaml can handle that by
making the distinction between 'chatty/harmless' events and otherwise.

In short, karaml is opinionated about layers and modifiers, and is designed to
act with zero delay given that most maps can be handled by reaching another
layer via tap-to-toggle or hold-to-enable. With this in mind, it tries to
reduce the need to manually specify 'companion' mappings for layer toggling,
e.g. for an 'x sets y = 1 if variable y = 0' mapping, karaml will
automtaically generate a 'x sets y = 0 if variable y = 1' mapping, and
for 'x sets y = 1 if x is held down', karaml will automatically generate 'x
  sets y = 0 if x is released'.

I try to handle as many other cases as possible in a concise manner in the
karaml style, but as a fallback, a `json:` map can be added to the config to
integrate a regular Karabiner JSON config (with minor YAML modifications).
In fact, you could just use karaml as a way to write a regular Karabiner
config in YAML but with less commas and little to no quotation marks.


## 🔩 Requirements

- Python >= 3.7

This program was written while using Karabiner-Elements 14.11.0 and MacOS 12.5.1

## 📦 Installation

Clone this repo and install with `pip` in your terminal:

```
git clone https://github.com/al-ce/karaml.git
cd karaml
pip install .
```

## 🚀 Usage

After you've made a well-formed karaml config, open your terminal app.

The `karaml` command requires one positional argument: the name of the yaml
file with your karaml config in the current folder (or the relative/absolute
path to that file).

```bash
$ karaml my_karaml_config.yaml
```

If your karaml maps aren't mapped correctly, the program will raise an
exception and try to give you some information about what went wrong. The error
system needs improvement - working on it!


## CLI prompt

Without any optional arguments, you will be prompted to make a configuration
choice:

```
$ karaml my_karaml_config.yaml
Reading from: my_karaml_config.yaml...

1. Update karabiner.json with my_karaml_config.yaml
2. Update complex modifications folder with my_karamlconfig_.yaml.
   Writes to: karaml_complex_mods.json
3. Quit
```

`1.` updates your karabiner.json file directly, either creating a new profile or
updating an existing one depending on the `profile_name` key in your config.
Before every update, karaml makes a backup copy of your previous 
`karabiner.json` in the `automatic_backups` folder. This can add up! But I
didn't want to risk a bug in the program destroying your config.


`2.` writes a json file to your karabiner complex modifications folder which
you can will appear in the Karabiner GUI. Then you can enable or disable layers
individually (or enable them all at once). The file is named
`karaml_complex_mods.json` by default, but you can change this in your karaml
config with the `title` key, (and so, easily switch between rulsets).


`3.` quits the program.

### -k mode

By passing the `-k` flag, you will bypass the prompt and karaml will update your karabiner.json file directly.
```bash
$ karaml my_karaml_config.yaml -k
```

### -c mode

By passing the `-c` flag, you will not be prompted and karaml will update your complex modifications folder directly.
If you're updating an old complex rule set, you'll have to remove the old complex modifications and re-enable the updated ones, as you would normally.
No backup files will be created for complex modifications, but you will get a confirmation prompt to confirm the overwrite/update. If you do not provide a `title` map in your yaml config, karaml will default to writing/updating the 'Karaml rules' ruleset.

```bash
$ karaml my_karaml_config.yaml -c
```

### -d (debug) mode

If there are malformed maps in your config, by default karaml prints you an
error message and quits. By adding the `-d` flag, you can see the full stack
trace of the error. If you're making a map that should work, either because
it's a feature you think should be implemented or because you found a bug, 
please add the stack trace in an issue!


## 🌱 TODO

- Protect against double maps in the same layer (accidental overwrites)
- More condition types (`foremost_application_if`, `device_if`, etc.)
- `from.simultaneous_options`
- `to_delayed_action`
- `halt` option for `to_if_held_down` and `to_if_alone`
- More helpful configuration error messages


## 🔭 Alternatives

- @mxstbr's [Karabiner configuration generator](https://github.com/mxstbr/karabiner) written in TypeScript
- [Goku](https://github.com/yqrashawn/GokuRakuJoudo)
