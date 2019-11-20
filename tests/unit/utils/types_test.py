"""
Tests for the types module
"""

import pytest

from bluebird.utils.types import is_valid_seed


def test():
    pytest.xfail("Not implemented")


def test_is_valid_seed():
    """Tests for the is_valid_seed function"""

    assert not is_valid_seed(-1)
    assert is_valid_seed(0)
    assert is_valid_seed(123)
    assert not is_valid_seed(2 ** 32)
