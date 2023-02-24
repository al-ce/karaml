import argparse

from karaml.file_writer import update_karabiner_json, write_complex_mods_json
from karaml.karaml_config import KaramlConfig


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "config_file",
        # dest="config_file",
        help="The Karaml config file to read from in the current directory. "
        "If the file is not in the current directory, provide the full path. "
        "If the file is in the current directory, provide only the file name. "
        "This argument is required.",
        action="store",
        type=str,
    )

    parser.add_argument(
        "-c",
        dest="complex_mods_output",
        help="Add/update the complex modifications folder to include the "
        "Karaml config passed as an argument. Takes an optional argument as "
        "the name of the file to write to. "
        "Defaults to `karaml_complex_mods.json`",
        action="store",

    )

    parser.add_argument(
        "-k",
        dest="k_profile",
        help="Add/update the karabiner.json file's proflies list to include "
        "the Karaml config passed as an argument",
        action="store_true",
    )

    parser.add_argument(
        "-hd",
        dest="hold_down",
        help="The flavor of hold to use. Default is 'to', but setting this "
        "flag changes it to 'to_if_held_down'",
        action="store_true",
    )

    args = parser.parse_args()
    config_file, complex_mods_output, k_profile, hold_down = vars(
        args).values()

    # For those who want to update their karabiner.json automatically,
    # set k_profiles (-K or --k)
    # This creates a backup of your karabiner.json on EACH run in the
    # automatic_backups folder.

    # For those who want to manage rules from assets/complex_modifications,
    # set complex_mods (-C or --c)

    print(f"\nReading from: {config_file}...\n")

    hold_flavor = "to" if not hold_down else "to_if_held_down"
    karaml_config = KaramlConfig(config_file, hold_flavor)

    if complex_mods_output:
        write_complex_mods_json(karaml_config, complex_mods_output)

    if k_profile:
        update_karabiner_json(karaml_config)

    if complex_mods_output or k_profile:
        print("Done!\n")
        return

    while True:
        print(f"  1. Update karabiner.json with {config_file}")
        print(f"  2. Update complex modifications folder with {config_file}.\n"
              "     Writes to: karaml_complex_mods.json")
        print("  3. Quit")
        choice = input("\nCommand: ")

        if choice == "1":
            update_karabiner_json(karaml_config)
            break
        elif choice == "2":
            write_complex_mods_json(karaml_config, "karaml_complex_mods.json")
            break
        elif choice in ["3", "q"]:
            print("Goodbye!")
            break
        else:
            print("Invalid choice.\n")


if __name__ == "__main__":

    main()
