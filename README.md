# karaml 🍮


**karaml** (**_Kara_**biner in ya**_ml_**) lets you write and maintain a
virtual layers-based [Karabiner-Elements](https://karabiner-elements.pqrs.org/) keyboard customization
configuration in YAML. It uses Python to translate the yaml into
Karabiner-compatible JSON.

karaml is based on the philosophy of [mxstbr](https://github.com/mxstbr)'s
layer-centered Karabiner [config](https://github.com/mxstbr/karabiner), and my
thanks goes to to [mxstbr](https://github.com/mxstbr) and
[yqrashawn](https://github.com/yqrashawn/) for the inspiration for this
project. Immense thanks to [tekezo](https://github.com/tekezo) for
Karabiner-Elements (consider
[sponsoring/donating](https://github.com/sponsors/tekezo)).

```yaml
# Default layer, does not require activation
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

  <a-h>: string(hello world) # Send multiple chars without concatenating with +

  # backspace/left on tap, MacOS/Kitty hints on hold/release, depending on frontmost app
  <c-h>: {
      # Notification with Karabiner-Style popup
      unless Terminal$ kitty$: [backspace, 'notify(idh, My MacOS Shortcut Hints)', 'notifyOff(idh)'],
      # Notification with AppleScript popup
      if Terminal$ kitty$: [left, 'shnotify(My Kitty Shortcuts, ==Kitty==)']
      }

# condition 'nav_layer' must be true for the following maps
/nav/:
  <(x)-h>: left               # vim navigation with any optional mods
  <(x)-j>: down
  <(x)-k>: up
  <(x)-l>: right
  s: [app(Safari), /sys/]     # Launch Safari on tap, /sys/ layer when held
  g: open(https://github.com) # Open link in default browser

# etc.
/sys/:
  <o-m>: [mute, null, mute]  # Mute if held/key down, unmute if released/key up
  k: play_or_pause
  "}": fastforward
  u: shell(open -b com.apple.ScreenSaver.Engine) # Start Screen Saver

# JSON integration
json:
  - {
      description: 'Right Shift to ) if tapped, Shift if held',
      from: { key_code: right_shift },
      to: { key_code: right_shift, lazy: true },
      to_if_alone: { key_code: 9, modifiers: [shift] },
      type: basic,
    }
```


## ✨ Features

- Complex modifications on a single line of yaml so you can create and update keymaps quickly
- Events for when a key is tapped, held, and released defined by position in an
  array (rather than k/v pairs)
- Simple schema for requiring mandatory or optional modifiers in a pseudo-Vim
  style
- Multiple frontmost-app conditional remaps in a single yaml map
- Aliases for symbols, shifted keys, and complex names (e.g.
  `grave_accent_and_tilde` → `grave`, `left_shift` + `[` → `{` )
- 'Special event' shorthands, e.g. app launchers, shell commands,
  notifications, and more
- Accepts regular Karabiner JSON in an 'appendix' table so all cases Karaml
  can't or doesn't plan to handle can still be in one config
- Automatically update your `karabiner.json` or write to the complex
  modifications folder and import with the Karabiner GUI - no need to handle
  any files other than your `.yaml` config
- Checks and formatting hints for your `.yaml` file - karaml will try not to
  let you upload a config that doesn't create a working modification, and tell
  you why (no more hunting for typos or missing/extraneous commas in a large JSON object)


## ❓ Why this project

The `karabiner.json` file can be hard to manage and visualize as it grows, as
the JSON format requires a lot of lines, carefully managed opening and closing
quotes, brackets, and commas, and repetitive conditional logic.

**karaml** tries to simplify this by providing a more readable, maintainable,
and easy to adjust format in YAML. This means making some trade-offs in
completeness of features, but I try to come close with the goal of balancing
features and configuration simplicity. To prevent the need for maintaining
multiple configurations if karaml falls short of your needs, karaml also
supports an 'appendix' table for any Karabiner-compatible JSON that can't be
expressed in karaml.

### Why YAML?

- Easy to maintain: no mandatory quotes, but quotes can simplify escaping
  troublesome characters; minimal or no use of brackets around keys/values
- [Easy to learn](https://learnxinyminutes.com/docs/yaml/) and easy to read
- A superset of JSON which allows us to fall back to JSON if wanted/needed
- Lets you leave comments for descriptions or notes to yourself!


## ⚡️ Quickstart

If you're unfamiliar with YAML, take a look at this handy
[guide](https://learnxinyminutes.com/docs/yaml/).

After [installing](#-installation), take the [sample YAML
configuration](./docs/sample_configuration.yaml) and use it as a template for
your own. The sample config has comments to explain karaml syntax.

For more detailed explanations, follow the [configuration
guide](/docs/config_guide.md) and read the [YAML
Configuration](#️-yaml-configuration) section of this document.

For a cleaner, less commented on example, see one of my configurations
[here](./docs/al-ce_config.yaml). Follow the [usage instructions](#-usage)
below to convert your karaml config to Karabiner-JSON with the command-line
tool (written in Python).

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
of convention. Maps in the `/base/` layer don't check for conditions.

To add additional events or options to your maps, put them in a YAML array or
sequence.

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

To add modifiers to a primary key, follow the format `<modifiers-primary_key>`.
Join multiple modifiers without any separation, but wrap optional modifiers in
parens.

Whether the optional set in parens comes first or last doesn't matter, e.g.
`<(c)os-g>` and `<os(c)-g>` are both valid. But a single set of optional
modifiers in parens must be to the right or left of *all* mandatory modifiers
(if there are any mandatory modifiers).

Left side modifiers are lowercase, right side modifiers are uppercase.


| key_code     | karaml | --- | key_code | karaml |
| ------------ | ------ | --- | --------- | ------ |
| `left_control` | `c`  | --- | `right_control` | `C`  |
| `left_shift`   | `s`  | --- | `right_shift`   | `S`  |
| `left_option`  | `o`  | --- | `right_option`  | `O`  |
| `left_command` | `m`  | --- | `right_command` | `M`  |
| `control`      | `r`  | --- | `control`       | `R`  |
| `shift`        | `h`  | --- | `shift`         | `H`  |
| `option`       | `a`  | --- | `option`        | `A`  |
| `command`      | `g`  | --- | `command`       | `G`  |

Examples:
- `<c-h>` → `left_ctrl` + `h` 
- `<(x)-h` → `h` (with any optional modifiers)
- `<mOC(s)-h>` → `left_cmd` + `right_opt` + `right_ctrl` + `left_shift` (optional) + `h`
- `<(s)mOC-h>` →   (same as above) 
- `<g(arh)-h>` → `cmd` (mandatory) + `option` + `control` + `shift` (optional) + `h`
- `<(arh)g-h>`   (same as above)


### Key-Code Aliases

You can follow the explicit mapping for any key (e.g. `<s-1>` → `!`), or use
these available aliases. Be mindful in your YAML config that some characters
need to be escaped or wrapped in quotes to be recognized as strings.


| karaml alias | Karabiner key_code            |
| ------------ | ----------------------------- |
| enter        | return_or_enter               |
| CR           | return_or_enter               |
| ESC          | escape                        |
| backspace    | delete_or_backspace           |
| BS           | delete_or_backspace           |
| delete       | delete_forward                |
| space        | spacebar                      |
| ' ' (space)  | spacebar                      |
| -            | hyphen                        |
| underscore   | hyphen + shift                |
| \_           | hyphen + shift                |
| =            | equal_sign                    |
| plus         | equal_sign + shift            |
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
| !            | 1 + shift                     |
| @            | 2 + shift                     |
| #            | 3 + shift                     |
| $            | 4 + shift                     |
| %            | 5 + shift                     |
| ^            | 6 + shift                     |
| &            | 7 + shift                     |
| *            | 8 + shift                     |
| up           | up_arrow                      |
| down         | down_arrow                    |
| left         | left_arrow                    |
| right        | right_arrow                   |
| pgup         | page_up                       |
| pgdn         | page_down                     |
| kp-          | keypad_hyphen                 |
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

#### Mutli-Modifier aliases:

| karaml alias | Karabiner key_code            |
| ------------ | ----------------------------- |
| hyper        | right_shift + right_option + right_command + right_control |
| ultra        | right_shift + right_option + right_command + right_control + fn |
| super        | right_shift + right_command + right_control |


Feel free to suggest other aliases/better names. In the future, I would like to
add a way to define your own aliases in the config file.


#### *MISSING ALIASES*:

- `+`, since it's used to join multiple key codes and I need
to figure out a way around that. Use `plus` in the meantime
- `kp+` for the same reason, so use `kpplus` as an alternate



### Simultaneous from-keys, multiple to-events, requiring multiple layers

To get simultaneous from events or multiple to events, i.e. in Karabiner-JSON:
```json
  {
    "from": {
      "simultaneous": [
            { "key_code": "j" },
            { "key_code": "k" }
        ]
    },
    "to": [
          { "key_code": "h" },
          { "key_code": "l" },
      ],
  }

```
Join valid key codes or aliases in any part of the YAML map with a `+`. This is
'whitespace agnostic', so `j+k`, `j + k`, and `j+k + l` etc. are all valid.

```yaml
/base/:
  j+k: h+l
  <c-j>+k: [escape, '/nav/ + notify(idn, Nav Layer on!)', 'notifyOff(idn)']

```

This also applies to joining layers if you want to enable two layers at once.
Note that whichever layer comes later in the config will take priority if
there are conflicting keys. In the following example, the `s` of the `/sys/`
layer will take priority over the `s` of the `/fn/` layer, and the
non-conflicting keys will all work as intended.

```yaml
/base/:
  <a-caps_lock>: [null, /fn/ + /sys/]  
/fn/:
  a: f1
  s: f2
  d: f3
/sys/:
  e: volume_down
  r: volume_up
  s: app(System Preferences)
```


Alternatively, for sending multiple singe characters, you can use `string()`.
See: [string special event function](#strings)

### Special Event Functions

Shorthands for common-use events. Some are just
[to.shell_command](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/shell-command/)
events in disguise.


#### App Launchers

`app(app_name)`

Pass an app name (as it appears in your Applications folder) as an argument to
`app()`. I like using these in my `/nav/` layer for quick access, but you might
want these in a standalone `/apps/` layer.

```yaml
/nav/:
  f: app(Firefox)
```

#### Open Browser Link

`open(url)`

Open a url with your default browser.

```yaml
/base/:
  <o-g>: open(https://github.com)

```

#### Shell Commands

`shell(shell command)`

Pass a [shell
command](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/shell-command/)
as an argument to `shell()`. This is what the app() and open() 'functions' are
actually doing under the hood. Please suggest other useful shorthands of shell
commands that we could add!

```yaml
/sys/:
  grave: shell(open ~)
```

#### Input Sources

```
input(lang_regex)
input({"language": "regex", "input_source_id": "regex", "input_mode_id": "regex" })
```

Either pass a language regex as an argument to `input()` to select the first
available input source that matches the regex, or pass a string representing a
JSON object with all the valid Karabiner fields as specified
[here](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/select-input-source/).

```yaml
/sys/:
  <o-k>+e: input(en)  # Set English input source
                      # Set a Greek keyboard based on source id
  <o-k>+g: 'input({   
            "input_source_id": "com.apple.keylayout.GreekPolytonic",
            "language": "el" 
            })'       # note the use of single quotes around the rhs to escape
                      # double quotes and commas
```

#### Mouse Movement

`mouse(action, speed|multiplier)`

Using the [to.mouse_key
event](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/mouse-key/),
you can pass a two arguments that represent a key/value pair of movement/speed,
or the speed_multiplier key and its multiplier value. If you want to assign
multiple mouse events to the mapping, you can pass a string representing a JSON
object matching the Karabiner specs, just like with input sources.

```yaml
/mouse/:
  m: mouse(x, -2000)
  n: mouse(y, 2000)
  e: mouse(y, -2000)
  i: mouse(x, 2000)
  <c-m>: mouse(horizontal_wheel, 100)
  <c-n>: mouse(vertical_wheel, -100)
  <c-e>: mouse(vertical_wheel, 100)
  <c-i>: mouse(horizontal_wheel, -100)
  s: mouse(speed_multiplier, 2.5)
```

#### Set Mouse Cursor Position

`mousePos(x, y, screen)`

Wraps around the [to.software_function.set_mouse_cursor_position](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/software_function/set_mouse_cursor_position/)
event. The `x` and `y` arguments are mandatory, the `screen` argument is
optional, and all three must be integers. The `screen` argument is the screen
number, starting from 0. If you don't specify a screen, the cursor will be
moved to the same screen as the current mouse position.

```yaml
/mouse/:
  '0': mousePos(0, 0)
  '<o-2>': mousePos(500, 500, 1)
```

#### Notifications (Karabiner Style)

`notify(id, message)`
`notifyOff(id)`

Shorthand for [to.set_notification_message](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/set-notification-message/)

The id is the reference for updating the notification with the message on
subsequent calls.

```yaml
/sys/:
  s:
    - app(System Preferences)
    - /sys/ + notify(sysNotification,"System Layer Enabled")
    - notifyOff(sysNotification)
```

There are a few ways to disable a notification. The easiest to use and remember
is to pass the notification id as the only arg to `notifyOff()`.

```yaml
notifyOff(id)
```

Otherwise, you can pass an empty string or `null` as the message arg to `notify()`.

```yaml
notify(id, null)
notify(id, "")
```


#### Notifications (AppleScript Style)

`shnotify(msg, title, subtitle, sound)`

`shnotify({"msg": "message", "title": "title", "subtitle": "subtitle", "sound": "sound"})`


Displays a notification using AppleScript by running a shell command in the
format:

```bash
osascript -e 'display notification "message" with title "title" subtitle "subtitle" sound name "sound"'
```

See the scriping documentation [here](https://developer.apple.com/library/archive/documentation/LanguagesUtilities/Conceptual/MacAutomationScriptingGuide/DisplayNotifications.html).

There are two ways to pass arguments to `shnotify()`. The first is to pass
positional arguments in the order of message, title, subtitle, and sound.

```yaml
/sys/:
  <o-1>: shnotify(text)  # message only
  <o-2>: shnotify(text, title)  # message and title
  <o-3>: shnotify(text, title, subtitle)  # message, title, and subtitle
  <o-4>: shnotify(text, title, subtitle, sound)  # message, title, subtitle, sound
  <o-5>: shnotify(text, null, null, sound)  # message and sound only
```

The second is to pass a string representing a JSON object with all the valid
AppleScript notification fields.

```yaml
/sys/:
  <o-6>: 'shnotify({
    "msg": "text",
    "title": "title",
    "subtitle": "subtitle",
    "sound": "sound"
    })'
  # With a dict, you can omit any fields you don't want to use
  <o-7>: 'shnotify({"msg": "text", "sound": "sound"})'
```

See the [sample configuration](#sample-configuration) for an example with
keyboard input source switching.

Sound names can be found at `/System/Library/Sounds/`
For more advanced notifications, try [terminal-notifier](https://github.com/julienXX/terminal-notifier) or [alerter](https://github.com/vjeantet/alerter) and pass the command as a `shell()` command.


#### Software Functions

`softFunc( {"function name": nested_dict} )`

Takes a string representing a JSON object with all the valid Karabiner fields
as specified
[here](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/soft-function/).

```yaml
/mouse/:
  'p+1': 'softFunc("set_mouse_cursor_position": {"x": 0, "y": 0, "screen": 0 })'
```

#### Sticky Modifiers

`sticky(modifier, toggle)`

Pass two arguments: the modifier to be held on the next keypress (must be a
valid modifier key code), and whether to toggle the modifier, turn it on, or
turn it off ('on | off | toggle')

```yaml
/base/:
  <o-right_shift>: sticky(left_shift, toggle)
```

#### Strings

`string(a string of valid key codes or aliases)`

Instead of mapping a key to type out a string of characters using the `+` joninig method, e.g. `git
checkout` like so:
```yaml
/base/:
<a-g>: g+i+t+space+c+h+e+c+k+o+u+t
```

You can use `string()` (though the above method is valid):

```yaml
/base/:
  <a-g>: string(git checkout )
```

The string must contain valid key codes or valid single-character aliases.
So, `[`, `?`, a blank space for `spacebar`, etc. will get interpreted
as characters, and `spacebar`, `kp-`, `left` etc. will get interpreted as a
literal string of chars, not their alias counterparts.

You can use a combination if you want to send non-single character events:
```yaml
/base/:
  <a-g>: string(git checkout main) + enter
```


#### Variables

The `var()` function takes two arguments: a variable name and a value (0 or 1).
See the [to.set_variable
documentation](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/set-variable/)

karaml intends variables to be handled as layers and automates some mappings
under the hood to streamline toggling and enabling layers, but the `var()`
function allows more granular control.

```yaml
/base/:
  <o-s>: var(sys_layer, 1) # This does not automatically create a corresponding
                           # toggle-off mapping. Don't get stuck in another layer!
```


### Frontmost-App Conditions

To set frontmost-app conditions, the from-key part of your map remains the
same, but your value becomes a dictionary (instead of the usual single string
or list/sequence).

```yaml
/layer/:
  from-key: {
      if regex regex ...: [when-tapped, when-held, etc.],
      unless regex regex ...: [etc.]
    }
```

The dictionary's keys must be in the form of either `if regex regex ...` or
`unless regex regex ...` where `regex` is a regex expression that matches the
bundle identifier of the app you want to match (read the [Karabiner
docs](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/conditions/frontmost-application/)
for more info). karaml will yell at you if your conditional term isn't `if` or
  `unless`. Every following substring separated by a space will be interpreted
  by karaml as a list (yaml supports lists in keys, but Python doesn't, so use
  a string here).

The dictionary's values are your usual karaml map values. Each k/v pair
represents a new map that includes the `frontmost_app_if/unless` conditional.

You can create as many unique keys as you want here, all of which will be tied
to the original 'from' key. Mind your regex and your capitalization!


```yaml
/base/:
  <c-u>: { unless Terminal$ iterm2$ kitty$: <g-backspace> }
  <a-O>: { unless Terminal$ iterm2$ kitty$: up + <g-right> + enter }
  <a-o>: { unless Terminal$ iterm2$ kitty$: <g-right> + enter }
  <a-g>: {
    # types 'git ' when tapped, 'checkout' when held if any of these apps are focused
    if Terminal$ iterm2$ kitty$: [string(git ), string(checkout)],
    if CotEditor$: <g-l> # 'go to line' alternate shortcut if CotEditor is focused
      }

```


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

Be mindful of the slight differences in syntax between yaml and JSON. Namely,
quotes are optional unless needed for escaping characters, elements of the
`json` map are separated as sequence item (a properly indented dash `-`
followed by a space), and no commas are used to separate those items.

***WARNING!***: in the layer mappings, karaml 'inspects' your configuration for
proper formatting - not just whether you wrote it in a syntax karaml can
intrepret, but also whether you used valid key codes, valid modifiers, etc.
Currently, karaml doesn't support these 'health checks' for the JSON extension map,
so karaml will just append whatever you put in there to the rule-set.

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
    to `~/.config/karabiner/automatic_backups/` as
    `karabiner.backup.TIMESTAMP.json`, every time (thirty of my ~6000 line
    Karabiner JSON backups add up to ~10MB, so check in every once in a while)
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
functions to a `to` dictionary (instead of `to_if_held_down`) provided
immediate switching between layers or enabling of modifier keys, since the `to`
dictionary doesn't wait for the `to_if_held_down_threshold_milliseconds` timeout. This means
sending the `to` event even when `to_if_alone` is sent , but so long as the
event is 'harmless', or not 'chatty', i.e. it is a layer, a modifier, or a
notfication, and so long as we set the `lazy` opt when necessary (e.g. for my
mapping of `enter` → `control` when held), this doesn't cause any significant
side effects.

When a 'chatty' event would have side-effects, or when sending an event on 'if
held down' following the relevant parameters is an explicit goal (rather than
just a way of distinguishing a tap from a hold), karaml can handle that by
making the distinction between 'chatty/harmless' events and otherwise. In these
cases, karml ***will*** place the 'when-held' event in the `to_if_held_down`
dictionary to prevent 'chatter' caused by events in the `to` dictionary.

In short, karaml is opinionated about layers and modifiers, and is designed to
act with zero delay given that most maps can be handled by reaching another
layer via tap-to-toggle or hold-to-enable. With this in mind, it tries to
reduce the need to manually specify 'companion' mappings for layer toggling,
e.g. for an 'x sets y = 1 if variable y = 0' mapping, karaml will automatically
generate a 'x sets y = 0 if variable y = 1' mapping, and for 'x sets y = 1 if x
is held down', karaml will automatically generate 'x sets y = 0 if x is
released'.

I try to handle as many other cases as possible in a concise manner in the
karaml style, but as a fallback, a `json:` map can be added to the config to
integrate a regular Karabiner JSON config (with minor YAML modifications). In
fact, you could just use karaml as a way to write a regular Karabiner config in
YAML but with less commas and little to no quotation marks.


## 🔩 Requirements

- Python >= 3.10

This program was written while using Karabiner-Elements 14.11.0 and MacOS
12.5.1

## 📦 Installation

Clone this repo and install with `pip` in your terminal:

```bash
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
karaml my_karaml_config.yaml
```

If your karaml maps aren't mapped correctly, the program will raise an
exception and try to give you some information about what went wrong. The error
system needs improvement - working on it!


### CLI prompt + modes

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

`1.` updates your karabiner.json file directly, either creating a new profile
or updating an existing one depending on the `profile_name` key in your config.
Before every update, karaml makes a backup copy of your previous
`karabiner.json` in the `automatic_backups` folder. This can add up! But I
didn't want to risk a bug in the program destroying your config.


`2.` writes a json file to your karabiner complex modifications folder which
you can import with the Karabiner GUI. Then you can enable or disable layers
individually, but you should them all at once to ensure your layer and mapping
priority is setup as intended. The file is named `karaml_complex_mods.json` by
default, but you can change this in your karaml config with the `title` key,
(and by doing so, you can easily switch between rulesets).


`3.` quits the program.

#### -k mode

By passing the `-k` flag, you will bypass the usual CLI prompt and karaml will
update your karabiner.json file directly (as always, creating a backup
beforehand).

```bash
karaml my_karaml_config.yaml -k
```


#### -c mode

By passing the `-c` flag, you will bypass the usual CLI prompt and karaml will
update your complex modifications folder directly. If you're updating an old
complex rule set, you'll have to remove the old complex modifications and
re-enable the updated ones, as you would normally. No backup files will be
created for complex modifications, but you will get a confirmation prompt to
confirm the overwrite/update. If you do not provide a `title` map in your yaml
config, karaml will default to writing/updating the 'Karaml rules' ruleset.

```bash
karaml my_karaml_config.yaml -c
```

#### -d (debug) mode

If there are malformed maps in your config, by default karaml prints you an
error message and quits. By adding the `-d` flag, you can see the full stack
trace of the error. If you're making a map that should work, either because
it's a feature you think should be implemented or because you found a bug,
please add the stack trace in an issue!

## 🪲 Known Issues / Bugs / Limitations
- Can't toggle layer in 'when-tapped' position if also set in 'when-held' position (e.g. `<a-f>: [/fn/, /fn/]` only enables the `/fn/` layer when held)
- `from.simultaneous_options` not yet supported (this one will be tricky)
- `to_delayed_action` not yet supported
- `halt` option for `to_if_held_down` and `to_if_alone` not yet supported
- ~~Can't add multiple shell-based pseudo-funcs in one mapping (see this [issue](https://github.com/al-ce/karaml/issues/3))~~

## 🌱 TODOs

- ~~Protect against double maps in the same layer (accidental overwrites)~~ user will be warned but not prohibited, see [5a66a39](https://github.com/al-ce/karaml/commit/5a66a39a75271cf27a88bf20f01df690b0688c12)
- More condition types (`device_if`, etc.)
- More helpful configuration error messages
- Define your own aliases
- Define your own functions
- ~~pseudo-function for typing out strings e.g. `string(git)`~~ Done!


## 🔭 Alternatives

- @mxstbr's [Karabiner configuration
  generator](https://github.com/mxstbr/karabiner) written in TypeScript
- [Goku](https://github.com/yqrashawn/GokuRakuJoudo)
