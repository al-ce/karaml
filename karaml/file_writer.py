from datetime import datetime
from json import dumps, loads
from pathlib import Path
from shutil import copyfile


def backup_karabiner_json(karabiner_path):
    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = karabiner_path / "automatic_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    karabiner_json = karabiner_path / "karabiner.json"
    backup_file = backup_dir / f"karabiner.backup.{current_time}.json"
    try:
        copyfile(karabiner_json, backup_file)
        print(f"Backed up karabiner.json to:\n{backup_file}\n")
        return True
    except FileNotFoundError:
        print(f"Could not find {karabiner_json}.\n"
              "Please check your karabiner.json path.\n"
              "By default, it is ~/.config/karabiner/karabiner.json\n"
              "Aborting attempt to update karabiner.json\n")
        return False


def basic_rules_dict(karaml_config) -> dict:
    return {"title": karaml_config.title,
            "rules": karaml_config.rules}


def match_profile_name(profiles: dict, profile_name: str):
    for profile in profiles:
        if profile["name"] != profile_name:
            continue
        return profile
    return None


def new_profile_dict(karaml_config, profile_name: str):
    with open("profile_template.json", "r") as f:
        profile_template = f.read()

    profiles_dict = loads(profile_template)
    template = update_complex_mods(profiles_dict, karaml_config)
    template["name"] = profile_name
    return template


def set_profile_name(karaml_config):
    profile_name = karaml_config.profile_name
    # To avoid accidental overwrite of previous profile, we use the current
    # time as as a unique identifier if no profile name is provided
    if not profile_name:
        current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        profile_name = "Karaml Profile " + str(current_time)
        print("No profile name specified, using: " + profile_name)
        print("Consider renaming the profile in Karabiner-Elements")
        is_set = False
    else:
        is_set = True
    return profile_name, is_set


def update_complex_mods(profile_dict: dict, karaml_config):
    karaml_dict = basic_rules_dict(karaml_config)
    complex_mods = profile_dict["complex_modifications"]
    complex_mods.update(karaml_dict)
    if karaml_config.params:
        complex_mods.update(karaml_config.params)
    return profile_dict


def update_karabiner_json(karaml_config):

    print("\nUpdating karabiner.json...\n")

    karabiner_path = Path("~/.config/karabiner").expanduser()
    if not backup_karabiner_json(karabiner_path):
        return
    with open(karabiner_path / "karabiner.json", "r") as f:
        karabiner_config = f.read()
    karabiner_dict = loads(karabiner_config)
    profiles = karabiner_dict["profiles"]
    profile_name, is_set = set_profile_name(karaml_config)
    found_profile = match_profile_name(profiles, profile_name)
    if is_set and found_profile:
        update_complex_mods(found_profile, karaml_config)
        update_detail = ""
    else:
        print(f"Could not find profile with name: {profile_name}.\n"
              "Creating new profile with determined name.\n")
        new_profile = new_profile_dict(karaml_config, profile_name)
        profiles.append(new_profile)
        update_detail = "with new "

    with open(karabiner_path / "karabiner.json", "w") as f:
        f.write(dumps(karabiner_dict, indent=4))
        print(
            f"Updated karabiner.json {update_detail}profile: {profile_name}.")


def write_complex_mods_json(karaml_config, to_file: str):
    if not to_file or not karaml_config:
        print("No destination file or karaml config provided. Aborting.")
        return
    complex_mods_path = Path(
        "~/.config/karabiner/assets/complex_modifications"
    ).expanduser()

    print("\nWriting complex modifications to:\n" +
          str(complex_mods_path / to_file) + "\n")

    if Path(complex_mods_path / to_file).exists():
        overwrite = None
        while overwrite not in ["Y", "N"]:
            overwrite = input(
                f"'{to_file}' already exists. Overwrite? [Y/N] "
            )
            if overwrite == "Y":
                print("Overwriting.")
            elif overwrite == "N":
                print("Aborting.")
                return
            elif overwrite == "q" or overwrite == "Q":
                print("Quitting.")
                exit()
            else:
                print("Please enter Y or N (uppercase) to continue"
                      "or q to quit.")

    rules_name = karaml_config.title if karaml_config.title else "Karaml rules"
    karaml_dict = basic_rules_dict(karaml_config)

    with open(complex_mods_path / to_file, "w") as f:
        f.write(dumps(karaml_dict, indent=4))
        print(f"Wrote '{rules_name}' complex modifications to {to_file}.")
