"""
Configuration for the integration issues tests
"""

import pytest


@pytest.fixture(scope="package", autouse=True)
def xfail():
    pytest.xfail("Issues tests need refactored")
