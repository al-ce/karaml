import pytest
import karaml.templates as templates


def test_translate_template():
    """
    Tests that the translate_template() function properly translates user
    mappings with default templates.

    This function should be receiving two args: the template name and the
    arguments to that template. e.g. if the user mapping is:

        ⌥ g: open(https://github.com/)

    Then the function should receive "open" and "https://github.com/".
    This should be returned as:

        ("shell_command", "open https://github.com")

    The default `TEMPLATES` list in karaml.templates should contain the
    default templates.
    """

    # Not a special event, so nothing to translate
    assert templates.translate_template("not_an_event", "some command") == (
        "not_an_event", "some command")

    assert templates.translate_template("app", "Firefox") == (
        "shell_command", "open -a 'Firefox'.app")

    assert templates.translate_template("input", "en") == (
        "select_input_source", {"language": "en"}
    )

    # TODO: add validation for select_input_source, mouse_key, soft_func,
    # etc. For now, it's the user's responsibility

    assert templates.translate_template("input", "'{'some': 'dictionary'}'") == (
        "select_input_source", {"language": "'{'some': 'dictionary'}'"}
    )

    # We don't actually check what the command/argument for 'open()' or
    # 'shell()'_is (e.g. is it a valid link or command, etc.) & trust the user

    assert templates.translate_template("mouse", "x, 2000") == (
        "mouse_key", {"x": 2000}
    )

    assert templates.translate_template(
        "mouse",
        '''{
            "x": 2000,
            "y": 2000,
            "vertical_wheel": 2000,
            "horizontal_wheel": 2000,
            "speed_multiplier": 1.0
        }'''
    ) == (
        "mouse_key",

        {
            "x": 2000,
            "y": 2000,
            "vertical_wheel": 2000,
            "horizontal_wheel": 2000,
            "speed_multiplier": 1.0
        }
    )

    assert templates.translate_template("mousePos", "1, 2") == (
        "software_function",
        {"set_mouse_cursor_position": {"x": 1, "y": 2}}
    )
    assert templates.translate_template("mousePos", "1, 2, 3") == (
        "software_function",
        {"set_mouse_cursor_position": {"x": 1, "y": 2, "screen": 3}}
    )

    with pytest.raises(SystemExit) as inv_mouse_pos_test:
        # Invalid mousePos arguments: min 2
        templates.translate_template("mousePos", "1")
    assert inv_mouse_pos_test.type == SystemExit

    with pytest.raises(SystemExit) as inv_mouse_pos_test:
        # Invalid mousePos arguments: max 3
        templates.translate_template("mousePos", "1, 2, 3, 4")
    assert inv_mouse_pos_test.type == SystemExit

    with pytest.raises(SystemExit) as inv_mouse_pos_test:
        # Invalid mousePos arguments: integers only
        templates.translate_template("mousePos", "one, two")
    assert inv_mouse_pos_test.type == SystemExit

    # Test for proper whitespace-stripping
    assert templates.translate_template("notify", " some_id ,some_msg") == (
        "set_notification_message", {"id": "some_id", "text": "some_msg"}
    )

    assert templates.translate_template("notifyOff", "some_id") == (
        "set_notification_message", {"id": "some_id", "text": ""}
    )

    assert templates.translate_template(
        "shnotify",
        "message, some title, a subtitle, frog sound"
    ) == (
        "shell_command",
        "osascript -e 'display notification \"message\" with title \"some title\" subtitle \"a subtitle\" sound name \"frog sound\"'"
    )

    assert templates.translate_template("open", "https://github.com") == (
        "shell_command", "open https://github.com"
    )

    assert templates.translate_template("shell", "cd somedir/") == (
        "shell_command", "cd somedir/"
    )

    assert templates.translate_template("softFunc", "some_arg") == (
        "software_function", "some_arg"
    )

    sticky_values = ["on", "off", "toggle"]
    for v in sticky_values:
        assert templates.translate_template("sticky", f"left_shift, {v}") == (
            "sticky_modifier", {"left_shift": v}
        )
    unsupported_sticky_mods = [
        "caps_lock", "command", "control", "option", "shift"
    ]
    with pytest.raises(SystemExit) as inv_sticky_mod_test:
        for m in unsupported_sticky_mods:
            # assert not template.translate_event("sticky", f"{m}, on")
            templates.translate_template("sticky", f"{m}, on")
    assert inv_sticky_mod_test.type == SystemExit

    # Only 'on', 'off', and 'toggle' are supported for sticky values
    with pytest.raises(SystemExit) as inv_sticky_val_test:
        templates.translate_template("sticky", "left_shift, some_value")
    assert inv_sticky_val_test.type == SystemExit

    assert templates.translate_template("var", "some_layer, 1") == (
        "set_variable", {"name": "some_layer", "value": 1}
    )

    with pytest.raises(SystemExit) as inv_var_value_type:
        templates.translate_template("var", "some_layer, not_a_number")
    assert inv_var_value_type.type == SystemExit


def test_mouse_pos():
    """
    Test the mouse_pos() func that interprets the mousePos() template in the
    yaml config.
    """

    # Test that  malformed mousePos() template args raise a SystemExit
    # Tests that floats are not accepted
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        templates.mouse_pos("1.0,2")
    assert pytest_wrapped_e.type == SystemExit

    # Test that the system exits if there are too few or too many args
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        templates.mouse_pos("1")
    assert pytest_wrapped_e.type == SystemExit

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        templates.mouse_pos("1,2,3,4")
    assert pytest_wrapped_e.type == SystemExit

    # Test that the function raises an exception if the args are not all
    # integers
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        templates.mouse_pos("1,2,three")
    assert pytest_wrapped_e.type == SystemExit

    # Test well-formed mousePos() template args

    # Test that a two-arg string returns a two-key dict of x and y in the
    # correct order
    assert templates.mouse_pos("1,2") == {"x": 1, "y": 2}

    # Test that a three-arg string returns a three-key dict of x, y, and
    # screen in the correct order
    assert templates.mouse_pos("1,2,3") == {"x": 1, "y": 2, "screen": 3}

    # Tests that a two-arg string with whitespace returns a two-key dict of x
    # and y in the correct order
    assert templates.mouse_pos(" 3 , 4 ") == {"x": 3, "y": 4}
