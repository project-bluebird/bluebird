"""
Integration tests for MachColl
"""
import os

import pytest


def pre_integration_check():
    if not os.environ.get("NATS_PYPI_INDEX", None):
        pytest.fail("MachColl tests specified, but NATS_PYPI_INDEX not set")
