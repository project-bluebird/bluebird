"""
Basic test configuration
"""

import pytest


@pytest.fixture(scope="function", autouse=True)
def log_break():
    """
    Adds a line break in the debug log file before each test
    :return:
    """
    print()
    yield
    print(f"\n=== New test ===")
