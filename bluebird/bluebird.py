"""
Contains the BlueBird class
"""

import logging

from . import settings
from .api import FLASK_APP
from .cache import AC_DATA, SIM_STATE
from .client import CLIENT_SIM
from .metrics import setup_metrics
from .utils import TIMERS


class BlueBird:
	"""
	The BlueBird API client.
	"""

	def __init__(self):
		self._logger = logging.getLogger(__name__)
		self._logger.info(f'BlueBird init. {settings.SIM_MODE} mode')

		setup_metrics()

	def __enter__(self):
		return self

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""
		Stops the app and cleans up any threaded code
		"""

		self._logger.info("BlueBird stopping")

		for timer in TIMERS:
			timer.stop()

		CLIENT_SIM.stop()

	def connect_to_sim(self, sim_type, min_sim_version, reset_on_connect):
		"""
		Connect to the simulation server
		:return: True if a connection was established with the server, false otherwise.
		"""

		CLIENT_SIM.start()

		self._logger.info('Connecting to client...')

		try:
			# TODO Will need to refactor the host_event port into kwargs
			CLIENT_SIM.connect(hostname=settings.SIM_HOST, event_port=settings.BS_EVENT_PORT,
			                   stream_port=settings.BS_STREAM_PORT, timeout=1)
		except TimeoutError:
			self._logger.error(f'Failed to connect to {sim_type} server at '
			                   f'{settings.SIM_HOST}, exiting')
			CLIENT_SIM.stop()
			return False

		if CLIENT_SIM.host_version < min_sim_version:
			self._logger.error(
							f'BlueSky server of version {CLIENT_SIM.host_version} does not meet the minimum '
							f'requirement ({min_sim_version})')
			return False
		if CLIENT_SIM.host_version.major > min_sim_version.major:
			self._logger.error(
							f'BlueSky server of version {CLIENT_SIM.host_version} has major version greater '
							f'than supported in this version of client ({min_sim_version})')
			return False

		if reset_on_connect:
			CLIENT_SIM.reset_sim()

		SIM_STATE.start()
		return True

	def run(self):
		"""
		Start the Flask app. This is a blocking method which only returns once the app exists.
		"""

		self._logger.debug("Starting Flask app")

		AC_DATA.start()
		FLASK_APP.run(host=settings.BB_HOST, port=settings.BB_PORT, debug=settings.FLASK_DEBUG,
		              use_reloader=False)
