"""
Tests that no exceptions are thrown when modules are imported
"""

import importlib

import pytest

_MODULES = ["bluebird", "bluesky"]


@pytest.mark.parametrize("module", _MODULES)
def test_module_import(module):
    """
    Tests that the given module can be imported without errors
    :return:
    """

    importlib.import_module(module)


def test_run_script_import():
    """
    Tests that the top-level run.py script can be imported without errors
    :return:
    """

    try:
        import run  # pylint: disable=unused-import
    except ImportError as exc:
        pytest.fail(str(exc))