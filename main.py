from file_writer import update_karabiner_json, write_rules_json
from layer_karamlizer import KaramlConfig


def main():

    # For those who want to manage rules from assets/complex_modifications
    new_rules = True
    # For those who want to update their karabiner.json automatically
    # This creates a backup of your karabiner.json on EACH run in the
    # automatic_backups folder.
    update_profile = True

    # from_file = "karaml-spec.yaml"
    # to_file = "karaml.json"

    from_file = "my_karaml.yaml"

    print(f"\nReading from Karaml config: {from_file}...")

    to_rules_file = "mykaraml.json"

    hold_flavor = "to"
    # hold_flavor = "to_if_held_down"

    karaml_config = KaramlConfig(from_file, hold_flavor)

    if new_rules:
        write_rules_json(to_rules_file, karaml_config)

    if update_profile:
        update_karabiner_json(karaml_config)


if __name__ == "__main__":
    main()
