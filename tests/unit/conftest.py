"""
Test configuration for all unit tests
"""

import mock
import pytest


@pytest.fixture(scope="function", autouse=True)
def log_break():
    """Adds setup and teardown code around each unit test"""

    # Runs before each test

    # NOTE(RKM 2019-12-12) Call this beforehand in-case the test throws an exception
    mock.patch.stopall()

    print()

    # Runs the test
    yield

    # Runs after each test

    print(f"\n=== New test ===")
