# karaml
**karaml** (***Kara***biner in ya***ml***) lets you write and maintain a virtual layers-based Karabiner-Elements configuration in YAML.

A yaml-based implementation of the layout concepts in @mxstbr's Karabiner [config](https://github.com/mxstbr/karabiner).

## ✨ Features
- Complex modifications on a single line of yaml
- Map complex events (app launches, shell commands, etc.), enable layers (set variables), and require conditions with shorthand syntax
- Events for when a key is tapped, held, and released in a sequential array (rather than k/v pairs)
- Simple schema for requiring mandatory or optional modifiers in a pseudo-Vim style
- Sensible aliases for symbols, shifted keys, and complex names (e.g. `grave_accent_and_tilde` → `grave`, `left_shift` + `9` → `(`)
- Accepts regular Karabiner JSON in an 'appendix' table so all cases Karaml can't or doesn't plan to handle can still be in one config
- Automatically update your `karabiner.json` or write to the complex modifications folder and import manually

## ⚡️ Quickstart template
**karaml** is built around the concept of layers, which are top-level yaml keys in the format `/layername/`. All maps belong to a layer, including any modifications you add to your base layer. Layer order in the configuration matters: a key mapped in a 'higher' layer, i.e. a layer written later in the config, will override that same key in a 'lower-level' layer *if* that higher layer is active.

Use this simple configuration as a template with an eye to the layer staucture. If you're unfamiliar with yaml, take a few minutes to learn its [syntax](https://learnxinyminutes.com/docs/yaml/).

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
                                       # use its proper key_code.
  right_shift: [">", right_shift]      # Aliases are available for many keys, but not required.
                                       # `">"` is equivalent to `<s-period>` or `<s-.>`
                                       # Check README.md for available aliases.

  # Simultaneous from keys (or multiple to keys) are concatenated with `+`
  # You can add or omit spaces between concatenated keys - your choice!

  h + `: shell(open ~)
  <o-h>: h+e+l+l+o  

  # Enable layers using the format `/layername/` in the 'to' part of the modification

  right_control: /nav/                 # Tap-toggle nav layer.
  right_command: [null, /sys/]         # Hold to enable sys layer, release to disable.
                                       # No event on tap.

  end: /symnum/                        # Tap-toggle symnum layer.

  delete: [/sys/, <moc-left_shift>]    # to: toggle /sys/ layer when tapped, hyper when held`
                                       # This combination sets the hold key event to
                                       # "to_if_held_down" regardless of hold flavor
                                       # to prevent 'chatty' key events.

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

Without any optional arguments, you will be prompted to make a configuration choice:

```
Reading from Karaml config: {your_karaml_config_filename}.yaml...

1. Update karabiner.json with my_karaml.yaml
2. Update complex modifications folder with my_karaml.yaml.
   Writes to: karaml_complex_mods.json
3. Quit
```

`1.` updates your karabiner.json file directly, either creating a new profile or updating an existing one depending on the `profile_name` key in your config. Before every update, karaml makes a backup copy of your previous `karabiner.json` in the `automatic_backups` folder. This can add up! But I didn't want to risk a bug in the program destroying your config.

`2.` writes a json file to your karabiner complex modifications folder which you can will appear in the Karabiner GUI. Then you can enable or disable layers individually (or enable them all at once). The file is named `karaml_complex_mods.json` by default, but you can change this in your karaml config with the `title` key, (and so, easily switch between rulsets).

`3.` quits the program.

## -k mode

By passing the `-k` flag, you will not be prompted and karaml will update your karabiner.json file directly. This is the fastest way to update your config and make fast, experimental changes.

## -c mode

By passing the `-c` flag, you will not be prompted and karaml will update your complex modifications folder directly, but you will have to remove the old comflex modifications and enable the new complex modifications manually on every update. This is a more cautious and prudent approach. No backup files will be created for complex rules, but you will get a confirmation prompt to allow the program to overwrite a previous rule set (if it has the same name as an existing one).
