"""
Tests that no exceptions are thrown when modules are imported
"""
import importlib

import pytest


def test_module_import():
    """Tests that the given module can be imported without errors"""

    importlib.import_module("bluebird")


def test_run_script_import():
    """Tests that the top-level run.py script can be imported without errors"""

    try:
        import run  # noqa: F401
    except ImportError as exc:
        pytest.fail(str(exc))
