"""
Contains the BlueBird class
"""

import logging

from . import settings
from .api import FLASK_APP
from .cache import AC_DATA, SIM_STATE
from .client import CLIENT_SIM
from .utils import TIMERS


class BlueBird:
	"""
	The BlueBird API client.
	"""

	def __init__(self):
		self._logger = logging.getLogger(__name__)
		self.client_connected = bool

	def __enter__(self):
		return self

	def client_connect(self, reset_on_connect=False):
		"""
		Connect to the (BlueSky) simulation client
		:return: True if a connection was established with the client, false otherwise.
		"""

		CLIENT_SIM.start()

		self._logger.info('Connecting to client...')

		try:
			CLIENT_SIM.connect(hostname=settings.BS_HOST, event_port=settings.BS_EVENT_PORT,
			                   stream_port=settings.BS_STREAM_PORT, timeout=1)

			self.client_connected = True
		except TimeoutError:
			print('Failed to connect to BlueSky server at {}, exiting'.format(settings.BS_HOST))
			CLIENT_SIM.stop()
			return

		if reset_on_connect:
			CLIENT_SIM.reset_sim()

		SIM_STATE.start()

	def run(self):
		"""
		Start the Flask app. This is a blocking method which only returns once the app exists.
		"""

		AC_DATA.start()
		FLASK_APP.run(host=settings.BB_HOST, port=settings.BB_PORT, debug=settings.FLASK_DEBUG,
		              use_reloader=False)

	def __exit__(self, exc_type, exc_val, exc_tb):
		"""
		Stops the app and cleans up any threaded code
		"""

		LOGGER.info("BlueBird stopping")

		for timer in TIMERS:
			timer.stop()

		CLIENT_SIM.stop()
