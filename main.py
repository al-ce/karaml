from layer_karamlizer import LayerKaramlizer


def main():
    # from_file = "karaml-spec.yaml"
    # to_file = "karaml.json"

    from_file = "my_karaml.yaml"
    to_file = "mykaraml.json"

    hold_flavor = "to"
    # hold_flavor = "to_if_held_down"

    karamlizer = LayerKaramlizer(from_file, hold_flavor)
    karamlizer.write_json(to_file)


if __name__ == "__main__":
    main()
