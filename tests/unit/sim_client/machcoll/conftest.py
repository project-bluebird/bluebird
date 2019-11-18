"""
Test configuration module for the current package
"""

import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def check_machcoll_path_set():
    load_dotenv(verbose=True, override=True)
    if not os.getenv("MC_PATH", None):
        pytest.skip("MC_PATH not set - skipping tests!")
