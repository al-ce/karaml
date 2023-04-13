import pytest
from karaml.helpers import validate_mouse_pos_args


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
