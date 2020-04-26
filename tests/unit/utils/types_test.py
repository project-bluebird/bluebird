"""
Tests for the types module
"""
import pytest

import bluebird.utils.types as types


def test():
    pytest.xfail("Some tests not implemented")


def test_altitude():
    """Tests for the Altitude type"""

    assert types.Altitude(0)
    assert types.Altitude(123)
    assert types.Altitude(9999)
    assert types.Altitude("FL000")
    assert types.Altitude("FL123")
    assert types.Altitude("FL999")
    assert types.Altitude("FL1000")

    with pytest.raises(AssertionError, match="Altitude must be specified"):
        types.Altitude(None)

    for val in [-1, -1.0]:
        with pytest.raises(AssertionError, match="Altitude must be positive"):
            types.Altitude(val)

    for val in ["aaaa", "FL", "FL-123"]:
        with pytest.raises(
            AssertionError,
            match="Altitude must be a valid flight level when passed as a string",
        ):
            types.Altitude(val)


def test_is_valid_seed():
    """Tests for the is_valid_seed function"""

    assert not types.is_valid_seed(-1)
    assert types.is_valid_seed(0)
    assert types.is_valid_seed(123)
    assert not types.is_valid_seed(2 ** 32)
