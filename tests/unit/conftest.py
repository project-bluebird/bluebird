"""
Basic test configuration
"""

import pytest

from bluebird.logging import _LOGGER


@pytest.fixture(scope="function", autouse=True)
def log_break():
    """
    Adds a line break in the debug log file before each test
    :return:
    """

    _LOGGER.debug(f"\n=== New test ===")
