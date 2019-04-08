"""
Tests that no exceptions are thrown when modules are imported
"""

import pytest

_MODULES = ['bluebird', 'bluesky']


@pytest.mark.parametrize('module', _MODULES)
def test_module_import(module):
	"""
	Tests that the given module can be imported without errors
	:return:
	"""

	try:
		__import__(module)
	except ImportError as exc:
		pytest.fail(str(exc))
