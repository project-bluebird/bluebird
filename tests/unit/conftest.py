"""
Module provides fixtures for unit tests. PyTest specifically looks for fixtures in the file with
this name.

Provides a test_flask_client fixture, which tests can use to send requests and to interact with a
patched version of BlueBird.
"""

import pytest

import bluebird.api as bluebird_api
from bluebird.api.resources.utils import FLASK_CONFIG_LABEL, bb_app
from bluebird.cache import AcDataCache, SimState
from bluebird.client.client import ApiClient
from bluebird.logging import _LOGGER
from bluebird.metrics import setup_metrics
from tests.unit import SIM_DATA, TEST_DATA


@pytest.fixture(scope='function', autouse=True)
def log_break():
	"""
	Adds a line break in the debug log file before each test
	:return:
	"""

	_LOGGER.debug(f'\n=== New test ===')


@pytest.fixture
def test_flask_client():
	"""
	Creates a Flask test client for BlueBird, and adds the needed dependencies to the
	application config
	:return:
	"""

	assert len({len(x) for x in TEST_DATA.values()}) == 1, \
		'Expected TEST_DATA to contain property arrays of the same length'

	bluebird_api.FLASK_APP.config['TESTING'] = True
	test_client = bluebird_api.FLASK_APP.test_client()

	sim_state = SimState()
	ac_data = AcDataCache(sim_state)

	class TestBlueSkyClient(ApiClient):
		"""
		Mock BlueSky client for use in testing
		"""

		def __init__(self):
			super().__init__(sim_state, ac_data)
			self.last_stack_cmd = None
			self.last_scenario = None
			self.last_dtmult = None
			self.was_reset = False
			self.was_stepped = False
			self.seed = None
			self.scn_uploaded = False

		def send_stack_cmd(self, data=None, response_expected=False, target=b'*'):
			self._logger.debug(f'STACK {data} response_expected={response_expected}')
			self.last_stack_cmd = data

		def load_scenario(self, filename, speed=1.0, start_paused=False):
			self._logger.debug(f'load_scenario {filename} {speed} {start_paused}')
			self.last_scenario = filename
			self.last_dtmult = speed
			bluebird.cache.AC_DATA.fill(TEST_DATA)

		def reset_sim(self):
			self.was_reset = True

		def upload_new_scenario(self, name, lines):
			self._logger.debug(f'upload_new_scenario, {name}')
			self.scn_uploaded = True

		def step(self):
			self.was_stepped = True

	class TestBlueBird:
		# pylint: disable=too-few-public-methods
		"""
		Mock BlueBird app for testing
		"""

		def __init__(self, sim_state, ac_data):
			self.sim_state = sim_state
			self.ac_data = ac_data
			self.sim_client = TestBlueSkyClient()
			self.metrics_providers = setup_metrics(self.ac_data)

	with bluebird_api.FLASK_APP.app_context() as ctx:
		ctx.app.config[FLASK_CONFIG_LABEL] = TestBlueBird(sim_state, ac_data)
		bb_app().ac_data.fill(TEST_DATA)
		bb_app().sim_state.update(SIM_DATA)

	yield test_client
