"""
Module provides fixtures for unit tests. PyTest specifically looks for fixtures in the file with
this name.

Populates BlueBird AC_DATA with some test aircraft information for use in testing.
"""

import pytest

import bluebird.cache
from . import TEST_DATA


@pytest.fixture(scope='session', autouse=True)
def populate_test_data():
	"""
	Fills AC_DATA with the test data
	:return:
	"""

	assert len({len(x) for x in TEST_DATA.values()}) == 1, \
		'Expected TEST_DATA to contain property arrays of the same length.'

	bluebird.cache.AC_DATA.fill(TEST_DATA)
