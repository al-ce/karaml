# karaml
**karaml** (***Kara***biner in ya***ml***) lets you write and maintain a virtual layers-based Karabiner-Elements configuration in YAML.

A yaml-based implementation of the layout concepts in @mxstbr's Karabiner [config](https://github.com/mxstbr/karabiner).

## ✨ Features
- Complex modifications on a single line of yaml
- Map complex events, enable layers (set variables), and require conditions with simple syntax
- Events for when a key is tapped, held, and released in a sequential array with no keys
- Simple schema for requiring mandatory or optional modifiers
- Sensible aliases for symbols, shifted keys, and complex names (e.g. `grave_accent_and_tilde` → `grave`)
- Accepts regular Karabiner JSON in an 'appendix' table
- Automatically update your `karabiner.json` or write to the complex modifications folder and import manually

## ⚡️ Quickstart template
**karaml** is built around the concept of layers. All maps belong to a layer, including any modifications you add to your base layer.
Use this simple configuration as a template. If you're unfamiliar with yaml, take a few minutes to learn its [syntax](https://learnxinyminutes.com/docs/yaml/).

<details>
  <summary>Click to expand code block</summary>

```yaml

/base/:
  grave: escape           # from_key: to_key (simple modification)
  <o-w>: <o-backspace>    # 'w' with mandatory left_option to 'delete_or_backspace' with left_option
  <o-f>: <o-delete>
  <o-p>: <m-v>            # left_option + p to left_command + v

                          # Syntax is: <`modifier`-`key`>. Modifier indicators: 
                          #   s, o, m, c (left shift, option, command, control)
                          #   S, O, M, C (right shift, option, command, control)
                          #   h, a, g, r (shift, option, command, control [either side])
                          #   l, f, x    (caps_lock, fn, any)


  <(x)-enter>: [enter, left_control]   # from return_or_enter (any optional modifier)
                                       #   to enter when tapped, left_control when held

  left_shift: [<s-comma>, left_shift]  # When a modifier is the primary key being modified,
                                       # use its proper key_code
  right_shift: [">", right_shift]      # Aliases are available for many keys, but not required.
                                       # `">"` is equivalent to `<s-period>` or `<s-.>`
                                       # Check README.md for available aliases

  # Simultaneous from keys (or multiple to keys) are concatenated with `+`
  # You can add or omit spaces between concatenated keys - your choice!

  h + `: shell(open ~)
  <o-h>: h+e+l+l+o  

  # Enable layers using the format `/layername/` in the 'to' part of the modification
  end: /symnum/                        # to: symnum layer (tapped or held)
  delete: [/sys/, <moc-left_shift>]    # to: toggle /sys/ layer when tapped, hyper when held`
  <(x)-caps_lock>: [escape, /nav/]     # to: escape when tapped, nav layer when held
                                       # Wrap the 'from' key in <(x)-`from_key`> so keys in the
                                       # enabled layer can take any modifier.


# The following maps require the nav layer to be enabled
/nav/:

  <m-j>: <msc-j>             # Add multiple modifiers to a key
  <m-k>: <msc-k>             # from: left command + k to: left command, shift, control + k
  <m-h>: <msc-h>
  <m-l>: <msc-l>

                             # Enable a layer from another layer
  d: [pgdn, /win/]           # pgdn | win(dow control) sublayer
  u: pgup

  t: app(CotEditor)          # app(app_name) shorthand
  c: app(Kitty)
  f: [app(Firefox), /fn/]    # Launch Firefox | functions sublayer


  # Set variables (i.e. enable layers) more explicitly with 'var(var_name, value)'
  # Only necessary if you want to set a layer and send another event simultaneously
  # yaml sequences (equivalent to an array, but in a list form) are useful for readability
  s:
    - app(Safari)
    - var(sys_layer,1) + notify(sysNotification,"System Layer Enabled")
    - var(sys_layer,0) + notify(sysNotification,)


/win/:
  m: <cm-m>
  i: <cm-i>
  e: <cm-e>
  n: <cm-n>
  pgdn: <cm-pgdn>
  "h": <cm-h>      # yaml doesn't require quotes around strings, but it will accept them
  .: <cm-.>        # Some characters don't require escaping with `\`, or being surrounded by quotes  
  ",": <cm-,>      # Some do, and it depends on the context
  \,: <cm-,>       # This is the same map as above, but escaped instead of surrounded by quotes


/sys/:
  e: volume_increment
  n: volume_decrement
  m: mute

  # The third optional position in the array is for 'to_after_key_up' events.
  # Since 'to' events are interpreted positionally, a 'null' is required for
  # undefined events between defined events

  <o-m>: [mute, null, mute]    # Sends mute on press, sends mute again on release
  # <o-m>: [null, null, mute]    # Only send mute on release/after key up

  u: shell(open -b com.apple.ScreenSaver.Engine)   # shell command shorthand

  # Notification shorthand: notify(id, message)
  # Quotes are required if your notification is in an array
  # because of the comma separating the id and message args

  # Notification displays when held, disappears on release
  <o-i>: ["notify(idHello, Hello!)", null, "notify(idHello,)"]


# To require multiple conditions (conceptually equivalent to having two layer
# on at the same time), concatenate layers as you would keys, with '+'

/some_layer/+/some_other_layer/:
  caps_lock: caps_lock           # overrides the base layer's map


# If the Karaml style config is too limiting or if a rule gets too comlex to be
# worth it, you can append slightly modified JSON in the Karabiner JSON style
# to this YAML map. Differences:

# - Quotes are optional, but check the YAML docs for escaping rules
# - Instead of separating rules with commas, as you would in JSON, use the YAML
#   sequence syntax, which is a dash followed by a space, then the rule

json:
  - {
      # No quotes in this rule, but note the single quotes around the
      # description, required because of the comma, i.e. `if tapped,`

      description: 'Right Shift to > if tapped, Shift if held',
      from: { key_code: right_shift },
      to: { key_code: right_shift, lazy: true },
      to_if_alone: { key_code: period, modifiers: [right_shift] },
      type: basic,
    }
  - {
      "description": "Left Shift to < if tapped, Shift if held",
      "from": { "key_code": "left_shift" },
      "to": { "key_code": "left_shift", "lazy": true },
      "to_if_alone": { "key_code": "comma", "modifiers": ["left_shift"] },
      "type": "basic",
    }
```
</details>

## 📦 Installation
Clone this repo and install with `pip`
```
git clone https://github.com/al-ce/karaml.git
cd karaml
pip install .
```

## 🚀 Usage
**karaml** requires one positional argument: the name of the yaml file with your karaml config in the current folder (or the relative/absolute path to that file).
```bash
karaml my_karaml_config.yaml
```

--IN PROGRESS--

