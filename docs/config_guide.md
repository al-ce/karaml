## 📚 Guide to writing a karaml config

This will guide you through creating a karaml config with minimal explanation
of the concepts. Consider looking at the sample configuration
[here](./sample_configuration.yaml) first as it might be enough to get you
going.

### Create a blank file

Fire up your favorite text editor (preferably with syntax highlighting -
[CotEditor](https://coteditor.com/) is a great choice) and create a blank
`.yaml` file, e.g. `karaml.yaml`. Save it somewhere convenient, like your
karabiner config folder (`/Users/yourMacUsername/.config/karabiner`).

### The base layer and basic remaps

karaml is built around "virtual layers" or [virtual modifiers](https://karabiner-elements.pqrs.org/docs/json/extra/virtual-modifier/). All key maps
belong to a layer. This includes the `base` layer, which you need to set up to
reach any other layers, and which should be the first layer in your config.
Let's make some simple remaps.


```yaml
/base/:
  caps_lock: escape

  left_shift: [(, left_shift)]
  right_shift:
    - )
    - right_shift

  escape: [null, mute, mute]
```
Here we established our base layer, and we remapped three keys using consistent
indentation. The first is a simple remap - `caps_lock` becomes `escape` whether
it's tapped or held.

The next two are the classic space-cadet remaps. More complex modifications go
in a JSON-style ordered list or a YAML sequence, which is an indented list of
items starting with a dash and a space. Use whatever looks best to you in
different situations. What's important for karaml is the order:

```yaml
from_key: [ when_tapped, when_held, when_released ]
from_key:
  - when_tapped
  - when_held
  - when_released
```

So in the space-cadet maps, the shift-keys are remapped to `)` and `(` when
tapped, and to `right_shift` and `left_shift` when held.


In the final mapping, we turn the actual escape key into a 'mute when held'
button. Since karaml uses ordered lists to determine its 'to' events by index,
if we want the 'when_released' event to be registered, it needs to be placed in
the third position, so any unused positions need to be filled by `null`.

If you need to remap a number (not on the keypad), you need to wrap it in
quotes so that it's interpreted as a string.

```yaml
/base/:
  "0": "1"
```



### Modifier syntax

Notice that we can use `(` as an alias for what in Karabiner-JSON would be:

```json
{ "key_code": "9", "modifiers": ["left_shift"] }
```

`karaml` offers a few syntax options for adding modifiers to your complex
modification rule. For this guide, we'll stick to:

`{modifiers} | {primary key}`

With the pipe character `|` as the delimiter.

Let's rewrite the space-cadet remaps without the aliases:

```yaml
left_shift: [s | 9, left_shift]
```
So `s | 9` is equivalent to the Karabiner-JSON above.

See the
[aliases](https://github.com/al-ce/karaml/blob/main/README.md#key-code-aliases)
section in the `README` for available aliases. Let's add some more maps with modifiers:

#### Single Modifiers
```yaml
/base/:
  c | w: o | backspace # left_control + w to left_option + backspace
  o | q: escape        # left_option + q to escape
  O | q: g | q         # right_option + q to command (either side) + q
  r | h: backspace     # control (either side) + h to backspace

```

Pay attention to the difference in letter case. Lower case is for left-side
modifiers, upper case is for right-side. 
For side-ambivalent modifiers, either works. Here's a table of the modifier keys:

| Karabiner-JSON | karaml | --- | Karabiner-JSON | karaml |
| -------------- | ------ | --- | -------------- | ------ |
| `left_control` | `c`  | --- | `right_control` | `C`  |
| `left_shift`   | `s`  | --- | `right_shift`   | `S`  |
| `left_option`  | `o`  | --- | `right_option`  | `O`  |
| `left_command` | `m`  | --- | `right_command` | `M`  |
| `control`      | `r`  | --- | `control`       | `R`  |
| `shift`        | `h`  | --- | `shift`         | `H`  |
| `option`       | `a`  | --- | `option`        | `A`  |
| `command`      | `g`  | --- | `command`       | `G`  |

The aliases `r`, `h`, `a`, and `g` are for `contRol`, `sHift`, `Alt` (`option`), and `Gui` (`command`). If you're not a fan of this system, you could use equiavlent symbols:

| Unicode symbol | key_code       |
| -------------- | -------------- |
| `⌘`            | `command` |
| `⌥`            | `option` |
| `⌃`            | `control` |
| `⇧`            | `shift` |
| `‹⌘`            | `left_command` |
| `‹⌥`            | `left_option` |
| `‹⌃`            | `left_control` |
| `‹⇧`            | `left_shift` |
| `⌘›`            | `right_command` |
| `⌥›`            | `right_option` |
| `⌃›`            | `right_control` |
| `⇧›`            | `right_shift` |


So the above would become:

```yaml
/base/:
  ‹⌃ | w: ‹⌥ | backspace # left_control + w to left_option + backspace
  ‹⌥ | q: escape        # left_option + q to escape
  ⌥› | q:  ⌘ | q         # right_option + q to command (either side) + q
  ⌃ | h: backspace     # control (either side) + h to backspace
```

#### Multiple Modifiers

To add multiple modifiers to a map, simply string them together:

```yaml
  o | c: ms | c        # left_option + c to left_command + left_shift + c
```

What if we want to modify a modifier key? Then we use the proper Karabiner
key_code as the primary key.

```yaml
C | left_shift: gar | shift  # right_control + left_shift
                              # to command + option + control + shift (hyper)
```
Or, you can use the modifier symbol:

```yaml
C | ⇧: gar | shift  # right_control + right_shift
                              # to command + option + control + shift (hyper)
```

Hey, wait a minute! `⇧` is supposed to be for either side, and that makes no
sense as a primary key, because your shift keys' `key_code` is either
`left_shift` or `right_shift`! So shouldn't that symbol be `‹⇧`?

Well, I didn't want to prevent the user from using the cleaner option of just
`⇧`. So if the user doesn't specify a side when using one of those symbols *as
a primary key*, then it defaults to the *left* side.


#### Mandatory vs. Optional Modifiers

So far, all the modifiers we've added are mandatory.
Let's add a map that takes optional modifiers.

```yaml
/base/:
  # Left, right, and side ambivalent modifiers
  o | w: o | backspace
  m | q: escape
  C | q: m | q
  a | h: backspace

  # Multiple modifier
  o | c: ms | c
  C | right_shift: gar | shift

  # Optional modifiers
  (x) | enter: [enter, control]   # enter with any optional modifier
                                  # to enter when tapped, control when held

  (mocs) | enter: [enter, contol] # Effectively the same as 'any left side mod'
```

Optional modifiers are indicated by wrapping an optional modifier key in parentheses.

The most likely use case for optional modifiers is to let you add any modifier
optionally. In the example above, we remapped `enter` to `enter` when tapped,
and control when held. By adding the `(x)`/ 'optional-any' modifier, we can
press any modifier key before we hold enter and still get `control` plus the
optional modifier(s) as the output.

All optional modifiers go in the same set of parens. Whether that set comes
first or last in the mapping doesn't matter, but put the mandatory modifiers (if there are any) to
one side and the optional modifiers to the other.


```yaml
ms(oc) | enter: mocs | enter  # Mandatory cmd + shift, optional alt and control
(oc)ms | enter: mocs | enter  # (same as above)
```

#### Alternate syntaxes

Since the original release of karaml, alternate syntaxes are supported for
mappings with modifiers.

- Surrounding angle brackets (`<` and `>`)
- Whitespace between modifiers
- The `|` character can be used to separate the modifiers and the primary keys
- Any amount of whitspeace can be used to separate the modifiers and the primary keys (the final stretch of whitespace acts as the delimiter)
- Use unicode characters for modifier keys
- Define your *own* single character modifier aliases

```yaml
/base/:
  <ms-1>: shell(~/bash_scripts/my_script.sh)
  c-w: o-backspace # left_control + w to left_option + backspace
  c m o s - g: open(https://github.com) # hyper + g to open github
  cm | o: /open/  # left_control + left_command + o toggles /open/ layer
  ⌃ ⌥ ⇧ ⌘  | s: string(git status) # hyper + s sends a string 'git status'
  ‹⇧ ⌃› | h + i: shnotify(hi)      # left_shift + right_control + h + i
                                   # triggers a macos notification 'hi'
```

See the `README` for more details on the alternate syntaxes.

### Simultaneous 'from' keys and multiple 'to' keys

Join multiple keys with a plus sign (`+`) in either the 'from' or 'to' part of
the map.

```yaml
j+k: escape
d + i + w: <o-backspace> + <o-delete>  # 'Delete Inner Word'
```

You can omit or add spaces between keys - whatever looks best to you.

For multiple single characters, you could do this:

```yaml
# Opt+g sends keystrokes 
a | g: [g+i+t+space, g+i+t+space+c+o+m+m+i+t+space+-+m+space+"+"+left]
```

But you can also use the `string()` template to make it look cleaner (more on
these templates later)

```yaml
a | g: [string(git ), string(git commit -m "") + left]
```

### Layers

Layers are karaml's way of visualizing the variable/condition system in
Karabiner. Let's get out of the base layer and create our 'nav' layer.

#### Enabling Layers

The two basic ways of enabling layers are to either enable them when a key is
pressed and held, then disable them on release, or toggle them on and off with
the same key (the other way is with the `var()` template, explained later).
Let's set up both, starting with the 'enable when held' method by enhancing our
`caps_lock` map.

```yaml
/base/:
  caps_lock: [escape, /nav/]
```
Place any `/layer_name/` in the second position. Now, every time we tap
`caps_lock`, we send `escape`; if we hold it, we enable the `/nav/`
layer, and if we release it, we disable that layer. No need to map anything in
the third 'when_released' position to toggle a layer off when you use a
`/layer_name/` style mapping - karaml handles that for you so you can keep your
config tidy and edit faster.

You'll find that layers (and modifiers) enabled *immediately* when they are
mapped in the second position, and you do not need to wait for the
`to_if_held_down_ms` threshold.

If you set `/nav/` in the first position or by itself, the 'from' key toggles
the layer on and off.

```yaml
caps_lock: /nav/
caps_lock: [/nav/, escape]
```
Both the above maps toggle `/nav/`. In the second map, `escape` does wait for
the `to_if_held_down_ms` threshold (and since the second map comes later, it
will override the first).

You do not need to make a corresponding 'toggle-off' mapping. Like
'enable-when-held' layers, karaml handles that for you.

You'll notice that when it comes to layers, karaml has some opinions on how they
should be handled. Read the documentation on `hold flavor` and `var()` for some
ways to get around these automations.


#### Configuring Layers

Let's set some maps that will only trigger if the layer is enabled.

```yaml
/nav/:
  (x) | h: left
  (x) | j: down
  (x) | k: up
  (x) | l: right
```

We mapped four keys, but what about all the keys that we didn't map? Those will
still work as they would in the base layer, because we didn't set a condition
that 'the `/nav/` layer must be off' for any of those keys (those undefined keys
in the `/nav/` layer are 'transparent'). So we could press and hold `caps_lock`,
move around with our new mappings, and press `backspace` without releasing caps
to delete some letters, even though we haven't mapped backspace in the `/nav/`
layer. Think of it as if all the mappings from the layer beneath are still 
active until they are overridden.

Which brings us to an important point: how you order your layers (and maps
within those layers) matters in karaml (because it matters in Karabiner).
Let's say you have the following configuration:

```yaml
/base/:
  caps_lock: [escape, /nav/]
  o | s: /sys/
  j+k: escape

/nav/:
  j: down
  k: up
  s: [null, /sys/]

/sys:
  j: volume_increment
  k: volume_decrement
```

- In the base layer, `j` and `k` behave normally unless they are pressed
  together (within the `simultaneous_threshold_milliseconds` parameter you set)
- If the `/nav/` layer is enabled, `j` and `k` will become the down and up 
arrow keys 
  - Since pressing `j+k` in the `/nav/` layer is equivalent to pressing
    `down+up`, that won't trigger `escape` - though that mapping is still
    active since we haven't overridden it yet! But we can't activate it in the
    `/nav/` layer since our `j` and `k` keys are remapped now.
- If the `/nav/` AND `/sys/` layers are enabled, `j` and `k` will be volume down/up,
  overriding any mappings from layers that came before. It doesn't matter if we
  enabled `/sys/` from the base or `/nav/` layer.


#### Requiring/enabling multiple layers

If you want to require multiple layers to be active for a specific mapping,
create a new layer that joins the layers with `+`. You'll need to place this
new multi-layer *after* the single ones.

To enable/toggle multiple layers, join them with `+` like you would for
keys/events.

```yaml
/base/:
  caps_lock : [escape, /nav/]
  o | s     : /sys/
  o | s + n : /sys/ + /nav/

/nav/:
  j: down
  s: /sys/

/sys:
  j: volume_decrement

/sys/ + /nav/:
  # The following keys are active only if BOTH /sys/ and /nav/ layers are active
  j: mute
```


### Templates

Karabiner supports different types of [to events](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/), which karaml (and other Karabiner-config tools) simplifies as much as
possible by accepting a template shorthand in the form `template_name(args)`

Check out the [descriptions](https://github.com/al-ce/karaml/blob/main/README.md#template)
in the `README.md` for more info. Most are straightforward, but you might want
to read up on `notify()`, `shnotify()`, and `var()`

```yaml
/base/:
  caps_lock: [escape, /nav/]
  o | s: var(sys_layer, 1)
  a | g: [string(git ), string(git commit -m "") + left]

/nav/:
  c: app(Kitty)
  f: app(Firefox)
  g: open(https://github.com)

  s:
    - app(Safari)
    - /sys/ + notify(sysNotification,"System Layer Enabled")
    - notify(sysNotification,)

  m: /mouse/

/sys/:
  o | s: var(sys_layer, 0)

  f: shell(open ~)
  v: shell(open -b com.apple.ScreenSaver.Engine)
  o | h: ["notify(idHello, Hello!)", null, "notify(idHello,)"]

  o | e: shnotify(English, ==KEYBOARD==) + input(en)
  o | g: 'shnotify(GreekPolytoniic, ==KEYBOARD==) + input({ "input_source_id": "com.apple.keylayout.GreekPolytonic", "language": "el" })'


/mouse/:
  spacebar: button1
  s | spacebar: button2

  h: mouse(x, -2000)
  j: mouse(y, 2000)
  k: mouse(y, -2000)
  l: mouse(x, 2000)

  c | h: mouse(horizontal_wheel, 100)
  c | j: mouse(vertical_wheel, 180)
  c | k: mouse(vertical_wheel, -180)
  c | l: mouse(horizontal_wheel, -100)

  s: mouse(speed_multiplier, 2.5)
  c | 1: 'softFunc("set_mouse_cursor_position": { "x": 0, "y": 0, "screen": 0 } })'
```

The `var(layer_name, value)` template is just a way to turn layers on and off
(i.e. set variable values) without karaml performing its opinionated automation
in the background, so, no automated mapping of 'toggle layer off' to the same
key if `var()` is in the tap position, and no automatic toggling off on release
if `var()` is in the hold position.


### to-opts and parameters

You can add a fourth-position item to the 'to' array to add the [lazy](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/lazy/), [repeat](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/repeat/), and [hold_down_milliseconds](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/to/hold-down-milliseconds/) options to a mapping.

```yaml
/base/:
  (x) | enter: [enter, control, null, [+lazy)] ]
  so | g: [ g + i + t + space, null, null, [-repeat] ]
  mocs | q: [ null, sm | q, null, [2000] ]
```

Prepend a `+` or `-` to the lazy or repeat options to set them to true or false. You can set both
options by separating them with a comma, e.g. `[+lazy, -repeat]`.

The hold_down_milliseconds option is an int, so don't put it in quotes.

You can add a *fifth* position item to add parameters to the mapping in the
form of a JSON object/dictionary. With this many items, I recommend using a
multiline YAML array.

```yaml
/base/:
  (x) enter:
    - enter
    - left_control
    - null
    - [+lazy] # - [ null ] or null to omit options
    - { a: 100, s: 50, d: 500, h: 100 }

```
We have aliases for the parameters dictionary keys to keep it neater:

- `a` → `basic.to_if_alone_timeout_milliseconds`,
- `h` → `basic.to_if_held_down_threshold_milliseconds`,
- `d` → `basic.to_delayed_action_delay_milliseconds`,
- `s` → `basic.simultaneous_threshold_milliseconds`,
- `m` → `mouse_motion_to_scroll.speed`,

Or you can pass the actual key names.

Again, if you want to omit any item in the array before the one you actually
want, you need to use `null` as a placeholder, so you could potentially have:

```yaml
  g + h: [ null, null, open(https://github.com), [ null ], { s: 150} ]
```

This is admittedly inefficient and tedious but I think it's easy to read, and
it's the tradeoff we make for ditching dictionary keys when we can.

### Frontmost-App If/unless conditions

Let's set some app-specific modifications. By using a dictionary instead of a
list or a single string, we can map the same key to have multiple functions
depending on the frontmost app, all without having to switch layers.

```yaml
/base/:
  c | u: { unless Terminal$ iterm2$ kitty$: g | backspace }
  a | O: { unless Terminal$ iterm2$ kitty$: up + g | right + enter }
  a | o: { unless Terminal$ iterm2$ kitty$: g | right + enter }
  a | g: {
    if Terminal$ iterm2$ kitty$: [string(git ), string(checkout)],
    if CotEditor$: g | l # 'go to line' alternate shortcut
      }

```

Above, `left_control + u` is remapped to `command + delete or backspace`
unless (if-not) the frontmost app is either Terminal, iTerm2, or Kitty (note
the difference in capitalization, per the bundle identifier that was shown to
me in the Karabiner [Event-Viewer](https://karabiner-elements.pqrs.org/docs/manual/operation/eventviewer/)).
`option + g` is remapped to typing out `git ` when tapped, `checkout` when held
if one of the terminal apps is in focus, but to `command + l` if CotEditor is in focus.

Since Python can't have mutable objects (like lists) as dictionary keys, we
need to pass a long string of space-separated sub-strings as the key,
with either `if` or `unless` as the first sub-string, followed by regex that
matches the application's bundle identifier as a dictionary value. Read the
Karabiner
[documentation](https://karabiner-elements.pqrs.org/docs/json/complex-modifications-manipulator-definition/conditions/frontmost-application/)
on this topic. Check out [regexone.com](https://regexone.com/) if you need a
regex brushup, but it's likely tagging the app name as it appears in the
Event-Viewer with a `$` should suffice.

karaml will print an error message and quit before doing anything with
your config if you try to pass anything other than `if` or `unless` as the
first sub-string of the condition.

Notice that in the last mapping, we added multiple conditions. Since it's a
dictionary(-like object) we can add as many as we like so long as they're
unique. 


### JSON extension appendix

You can append slightly modified JSON in the Karabiner JSON style to this YAML
map with these differences:

- Quotes are optional, but check the YAML docs for escaping rules
- Instead of separating rules with commas, as you would in JSON, use the YAML
  sequence syntax, which is a dash followed by a space, then the rule

This will be interpreted like a regular Karabiner modification.
If a rule gets too complex to be worth jumping through karaml hoops or there's
a bug that hasn't been worked out yet, I didn't want that to be the reason you
don't stick with karaml, so this gives you access to fully-featured
modifications for complicated cases.

```yaml
json:
  - {
      # No quotes in this rule, but note the single quotes around the
      # description, required because of the comma, i.e. `if tapped,`
      description: "Right Control to > if tapped, control if held",
      from: { key_code: right_control },
      to: { key_code: right_control, lazy: true },
      to_if_alone: { key_code: period, modifiers: [right_control] },
      type: basic,
    }
  - {
      "description": "Left Control to < if tapped, control if held",
      "from": { "key_code": "left_control" },
      "to": { "key_code": "left_control", "lazy": true },
      "to_if_alone": { "key_code": "comma", "modifiers": ["left_control"] },
      "type": "basic",
    }
```

### Profile names, rule-set title, and global parameters

At the top of your config, you can add some **optional** YAML maps that will
give your config a profile name, a complex-modifications rule-set title, and
global parameters that will apply to your profile. All these can exist in a
config regardless of how you use it. 

```yaml
# Profile Name: If one is not provided, one will be generated from the
# current Unix timestamp
profile_name:
  Karaml Config

# Optional: include title for ruleset (recommended)
title:
  KaramlConfig

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

If you don't set a profile name and choose the `1. Update karabiner.json`
option in the CLI, karaml will upload your config with a unique name using the
current Unix timestamp, e.g. `Karaml Profile 1677293783`, because I don't want
you to accidentally overwrite your previous profile (though a new backup of
your current profile is created every time you upload/update your config).

If you don't set a complex rule set and choose the `Update complex
modifications folder` option in the CLI, karaml will give your config the
default title `KaramlRules`. If a complex rule-set with the same title (yours
or the default) already exists, you'll be asked to confirm the overwrite.

You can have multiple profiles and rule-sets so long as you give
them different names, so naming them is recommended!

### Sample karaml configuration

See a sample configuration [here](./sample_configuration.yaml)
