"""
Module provides fixtures for unit tests. PyTest specifically looks for fixtures in the file with
this name.

Populates BlueBird AC_DATA with some test aircraft information for use in testing.
"""

import pytest

import bluebird.cache
import bluebird.client
from bluebird.client.client import ApiClient
from . import SIM_DATA, TEST_DATA


@pytest.fixture(scope='session', autouse=True)
def populate_test_data():
	"""
	Fills AC_DATA with the test data
	:return:
	"""

	assert len({len(x) for x in
	            TEST_DATA.values()}) == 1, 'Expected TEST_DATA to contain property arrays of the ' \
	                                       'same length.'

	bluebird.cache.AC_DATA.fill(TEST_DATA)
	bluebird.cache.SIM_STATE.update(SIM_DATA)


@pytest.fixture
def patch_client_sim(monkeypatch):
	"""
	Provides a patched BlueSky client and sets it as the CLIENT_SIM
	:param monkeypatch:
	:return:
	"""

	class TestClient(ApiClient):
		"""
		Mock BlueSky client for use in testing
		"""

		def __init__(self):
			super().__init__()
			self.last_stack_cmd = None
			self.last_scenario = None
			self.was_reset = False

		def send_stack_cmd(self, data=None, target=b'*'):
			self.last_stack_cmd = data

		def load_scenario(self, filename, speed=1.0):
			self.last_scenario = filename

		def reset_sim(self):
			self.was_reset = True

	monkeypatch.setattr(bluebird.client, 'CLIENT_SIM', TestClient())
