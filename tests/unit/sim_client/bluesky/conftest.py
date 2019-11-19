"""
Test configuration module for the current package
"""

import os

import pytest


@pytest.fixture(autouse=True)
def check_bluesky_path_set():
    if not os.getenv("BS_PATH", None):
        pytest.fail("Expected BS_PATH to be set")
