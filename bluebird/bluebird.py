"""
Contains the BlueBird class
"""

import logging

from bluebird import settings
from bluebird.api import FLASK_APP
from bluebird.cache import AC_DATA, SIM_STATE
from bluebird.client import CLIENT_SIM
from bluebird.utils import TIMERS

LOGGER = logging.getLogger(__name__)


class BlueBird:
	"""
	The BlueBird API client.
	"""

	@staticmethod
	def client_connect(reset_on_connect=False):
		"""
		Connect to the (BlueSky) simulation client
		:return: True if a connection was established with the client, false otherwise.
		"""

		CLIENT_SIM.start()

		LOGGER.info('Connecting to client...')

		try:
			CLIENT_SIM.connect(hostname=settings.BS_HOST, event_port=settings.BS_EVENT_PORT,
			                   stream_port=settings.BS_STREAM_PORT, timeout=1)


		except TimeoutError:
			print('Failed to connect to BlueSky server at {}, exiting'.format(settings.BS_HOST))
			CLIENT_SIM.stop()
			return False

		if reset_on_connect:
			CLIENT_SIM.reset_sim()

		SIM_STATE.start()
		return True

	@staticmethod
	def run_app():
		"""
		Start the Flask app. This is a blocking method which only returns once the app exists.
		"""

		AC_DATA.start()
		FLASK_APP.run(host='0.0.0.0', port=settings.BB_PORT, debug=settings.FLASK_DEBUG,
		              use_reloader=False)

	@staticmethod
	def stop():
		"""
		Stops the app and cleans up any threaded code
		"""

		LOGGER.info("BlueBird stopping")

		for timer in TIMERS:
			timer.stop()

		CLIENT_SIM.stop()
