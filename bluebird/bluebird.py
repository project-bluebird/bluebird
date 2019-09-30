"""
Contains the BlueBird class
"""

import logging

from bluebird import settings
from bluebird.api import FLASK_APP
from bluebird.cache import AcDataCache, SimState
from bluebird.client import ApiClient
from bluebird.metrics import setup_metrics


class BlueBird:
	"""
	The BlueBird application
	"""

	def __init__(self):
		self._logger = logging.getLogger(__name__)
		self._logger.info(f'BlueBird init - sim type: {settings.SIM_TYPE.name}, '
		                  f'mode: {settings.SIM_MODE}')

		# TODO Refactor these two into a single Simulation proxy class
		self.sim_state = SimState()
		self.ac_data = AcDataCache(self.sim_state)

		self.sim_client = None
		self._timers = []
		self.metrics_providers = setup_metrics(self.ac_data)

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""
		Stops the app and cleans up any threaded code
		"""

		self._logger.info("BlueBird stopping")

		for timer in self._timers:
			timer.stop()

		self.sim_client.stop()

	def connect_to_sim(self, min_sim_version, reset_on_connect):
		"""
		Connect to the simulation server
		:return: True if a connection was established with the server, false otherwise.
		"""

		# TODO Need to use this to construct the correct client type
		sim_type = settings.SIM_TYPE

		self.sim_client = ApiClient(self.sim_state, self.ac_data)
		self._timers.append(self.sim_client.start_timer())

		self._logger.info('Connecting to client...')

		try:
			# TODO Will need to refactor the host_event port into kwargs
			self.sim_client.connect(hostname=settings.SIM_HOST, event_port=settings.BS_EVENT_PORT,
			                        stream_port=settings.BS_STREAM_PORT, timeout=1)
		except TimeoutError:
			self._logger.error(f'Failed to connect to {sim_type.name} server at '
			                   f'{settings.SIM_HOST}, exiting')
			self.sim_client.stop()
			return False

		if self.sim_client.host_version < min_sim_version:
			self._logger.error(
							f'BlueSky server of version {self.sim_client.host_version} does not meet the '
							f'minimum requirement ({min_sim_version})')
			return False
		if self.sim_client.host_version.major > min_sim_version.major:
			self._logger.error(
							f'BlueSky server of version {self.sim_client.host_version} has major version '
							f'greater than supported in this version of client ({min_sim_version})')
			return False

		if reset_on_connect:
			self.sim_client.reset_sim()

		self._timers.append(self.sim_state.start_timer())
		return True

	def run(self):
		"""
		Start the Flask app. This is a blocking method which only returns once the app exists.
		"""

		self._logger.debug("Starting Flask app")

		# TODO This should be in connect_to_sim?
		self._timers.append(self.ac_data.start_timer())
		FLASK_APP.config['bluebird'] = self
		FLASK_APP.run(host=settings.BB_HOST, port=settings.BB_PORT, debug=settings.FLASK_DEBUG,
		              use_reloader=False)
