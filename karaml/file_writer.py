from datetime import datetime
from json import dumps, loads
from pathlib import Path
from shutil import copyfile
from karaml.karaml_config import KaramlConfig


def backup_karabiner_json(karabiner_path: Path) -> bool:
    """
    Backs up karabiner.json to automatic_backups folder.
    Returns True if backup was successful, False otherwise.
    """

    current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = karabiner_path / "automatic_backups"
    backup_dir.mkdir(parents=True, exist_ok=True)
    backup_dir_size = get_backup_folder_size(backup_dir)
    report_backup_folder_size(backup_dir, backup_dir_size)

    karabiner_json = karabiner_path / "karabiner.json"
    backup_file = backup_dir / f"karabiner.backup.{current_time}.json"
    try:
        copyfile(karabiner_json, backup_file)
        print("Backed up karabiner.json to:"
              f"\n~/{backup_file.relative_to(Path.home())}\n")

        return True
    except FileNotFoundError:
        print(f"Could not find {karabiner_json}.\n"
              "Please check your karabiner.json path.\n"
              "By default, it is ~/.config/karabiner/karabiner.json\n"
              "Aborting attempt to update karabiner.json\n")
        return False


def get_backup_folder_size(backup_dir: Path) -> int:
    """
    Returns the size of the backup folder in bytes.
    """
    size = 0
    for file in backup_dir.iterdir():
        if file.is_file():
            size += file.stat().st_size
    return size


def report_backup_folder_size(backup_dir: Path, size: int):
    """
    Reports the size of the backup folder in MB. Warns the user if the
    size is over 100 MB.
    """
    if size > 100000000:
        print("WARNING! Backup folder size is over 100 MB.")
    rounded_size = round(size / 1000000, 2)
    print(f"Backup folder size: {rounded_size} MB\n")


def basic_rules_dict(karaml_config) -> dict:
    return {"title": karaml_config.title,
            "rules": karaml_config.layers}


def match_profile_name(profiles: dict, profile_name: str) -> dict:
    """
    Returns the profile with the specified name if it exists in the list of
    Karabiner-Elements profiles. Otherwise, returns an empty dict.
    """
    for profile in profiles:
        if profile["name"] != profile_name:
            continue
        return profile
    return {}


def new_profile_dict(karaml_config, profile_name: str) -> dict:
    with open("profile_template.json", "r") as f:
        profile_template = f.read()

    profiles_dict = loads(profile_template)
    template = update_complex_mods(profiles_dict, karaml_config)
    template["name"] = profile_name
    return template


def set_profile_name(karaml_config: KaramlConfig) -> tuple[str, bool]:
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


def update_complex_mods(profile_dict: dict, karaml_config) -> dict:
    karaml_dict = basic_rules_dict(karaml_config)
    complex_mods = profile_dict["complex_modifications"]
    complex_mods.update(karaml_dict)
    if karaml_config.params:
        complex_mods.update(karaml_config.params)
    return profile_dict


def update_karabiner_json(karaml_config: KaramlConfig):
    """
    Updates karabiner.json with the karaml config. If no profile name is
    specified, a new profile is created with the current time as a unique
    identifier. If a profile name is specified, the profile with that name
    is updated. If no profile with that name is found, a new profile is
    created with the specified name.
    """

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
    """
    Writes the karaml config to a complex modifications json file. This
    file can be imported into Karabiner-Elements using the GUI.
    """
    if not to_file or not karaml_config:
        print("No destination file or karaml config provided. Aborting.")
        return
    complex_mods_path_str = "~/.config/karabiner/assets/complex_modifications"
    complex_mods_path = Path(complex_mods_path_str).expanduser()

    print("\nWriting complex modifications to:\n"
          f"{complex_mods_path_str}/{to_file}\n")

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
