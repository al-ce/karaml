# TODO: Migrate all helper tests to this file

import pytest

from karaml.helpers import check_and_validate_str_as_dict, validate_mouse_pos_args


def test_validate_mouse_pos_args():
    """
    Tests the validate_mouse_pos_args() function.
    The function takes one argument, which is a string of comma-separated
    integers. The function should raise an exception if the string is not
    well-formed.
    """

    # Test that well-formed strings are accepted.
    # Well-formed strings have 2 or 3 args, and all args are integers
    assert validate_mouse_pos_args("1,2") == 0
    assert validate_mouse_pos_args("1,2,3") == 0

    # Tests that floats are not accepted
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        validate_mouse_pos_args("1.0,2")
    assert pytest_wrapped_e.type == SystemExit

    # Test that the system exits if there are too few or too many args
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        validate_mouse_pos_args("1")
    assert pytest_wrapped_e.type == SystemExit

    with pytest.raises(SystemExit) as pytest_wrapped_e:
        validate_mouse_pos_args("1,2,3,4")
    assert pytest_wrapped_e.type == SystemExit

    # Test that the function raises an exception if the args are not all
    # integers
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        validate_mouse_pos_args("1,2,three")
    assert pytest_wrapped_e.type == SystemExit


def test_check_and_validate_str_as_dict():
    """
    Tests the check_and_validate_str_as_dict() function.
    The function takes a string as an argument and returns True if:
    - The string is intended to be a dict, which is indicated by the string
      starting with a '{' and ending with a '}'.
    - The contents of the brackets are key-value pairs separated by commas,
        where each key-value pair is separated by a colon.
    - The key for each key-value pair is a string.

    Returns False if the string is not intended to be a dict.
    Returns True if it passes all the checks mentioned above.
    Raises an exception and exits if any of the checks fail.
    """

    # Test that a well-formed dict string returns True
    valid_string = '{"hello": "world"}'
    valid_dict = {'hello': 'world'}
    assert check_and_validate_str_as_dict(valid_string) == valid_dict

    # Test that a string that is not intended to be a dict returns False
    assert not check_and_validate_str_as_dict("1,2")

    # Must have both an opening and closing bracket
    assert not check_and_validate_str_as_dict("{'hello': 'world'")
    assert not check_and_validate_str_as_dict("'hello': 'world'}")

    # Raise an exception if the key in a key-value pair is not a string
    with pytest.raises(SystemExit) as pytest_wrapped_e:
        check_and_validate_str_as_dict("{hello: 'world'}")
    assert pytest_wrapped_e.type == SystemExit
