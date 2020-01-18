"""
Test configuration module for the current package
"""
import os

import pytest


@pytest.fixture(autouse=True)
def check_machcoll_path_set():
    if not os.getenv("MC_PATH", None):
        pytest.skip("MC_PATH not set - skipping tests!")
