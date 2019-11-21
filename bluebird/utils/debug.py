"""
Utility functions for debugging
"""


def ASSERT_NOT_REACHED(msg: str) -> None:
    """Raises an AssertionError with the given message :^)"""
    assert False, msg
