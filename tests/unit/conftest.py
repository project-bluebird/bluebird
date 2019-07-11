"""
Module provides fixtures for unit tests. PyTest specifically looks for fixtures in the file with
this name.

Populates BlueBird AC_DATA with some test aircraft information for use in testing.
"""

import pytest

import bluebird.api as bluebird_api
import bluebird.cache
import bluebird.client
from bluebird.client.client import ApiClient
from . import SIM_DATA, TEST_DATA


@pytest.fixture
def client():
	"""
	Creates a Flask test client for BlueBird
	:return:
	"""

	bluebird_api.FLASK_APP.config['TESTING'] = True
	test_client = bluebird_api.FLASK_APP.test_client()

	yield test_client


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
			self.last_dtmult = None
			self.was_reset = False
			self.was_stepped = False
			self.seed = None

		def send_stack_cmd(self, data=None, response_expected=False, target=b'*'):
			self.last_stack_cmd = data

		def load_scenario(self, filename, speed=1.0, start_paused=False):
			self.last_scenario = filename
			self.last_dtmult = speed

		def reset_sim(self):
			self.was_reset = True

		def upload_new_scenario(self, name, lines):
			return None

		def step(self):
			self.was_stepped = True

	monkeypatch.setattr(bluebird.client, 'CLIENT_SIM', TestClient())
