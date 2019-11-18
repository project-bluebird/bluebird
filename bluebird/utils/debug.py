"""
Utility functions for debugging
"""


def ASSERT_NOT_REACHED(msg: str) -> None:  # pylint: disable=invalid-name
    """Raises an AssertionError with the given message :^)"""
    assert False, msg
