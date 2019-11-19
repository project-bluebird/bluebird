"""
Configuration for the metrics tests
"""

import pytest


@pytest.fixture(autouse=True)
def skip_for_now():
    pytest.xfail("Metrics tests need to be updated")
