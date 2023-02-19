from layer_karamlizer import LayerKaramlizer


def main():
    # from_file = "karaml-spec.yaml"
    # to_file = "karaml.json"
    from_file = "my_karaml.yaml"
    to_file = "mykaraml.json"
    # from_file = "test.yaml"
    # to_file = "test.json"

    karamlizer = LayerKaramlizer(from_file)
    karamlizer.write_json(to_file)


if __name__ == "__main__":
    main()

# TODO: Implement to: [ "lazy": bool ]
# TODO: Figure out yaml syntax for shift, control etc.
# (as opposed to left_shift, etc)

# TODO: Implement default parameters (100, 101, 500, 50/500)
