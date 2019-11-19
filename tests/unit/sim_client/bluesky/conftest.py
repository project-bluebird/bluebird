"""
Test configuration module for the current package
"""

import os

import pytest
from dotenv import load_dotenv


@pytest.fixture(autouse=True)
def check_bluesky_path_set():
    load_dotenv(verbose=True, override=True)
    if not os.getenv("BS_PATH", None):
        pytest.fail("Expected BS_PATH to be set")
