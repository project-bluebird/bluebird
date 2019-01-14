"""
Contains the BlueBird class
"""

from bluebird import settings
from bluebird.api import FLASK_APP
from bluebird.client import CLIENT_SIM
from bluebird.utils import TIMERS


class BlueBird:
	"""
	The BlueBird API client.
	"""

	@staticmethod
	def client_connect():
		"""
		Connect to the (BlueSky) simulation client
		:return: True if a connection was established with the client, false otherwise.
		"""

		try:
			CLIENT_SIM.connect(
							hostname=settings.BS_HOST,
							event_port=settings.BS_EVENT_PORT,
							stream_port=settings.BS_STREAM_PORT,
							timeout=1)

			return True

		except TimeoutError:
			CLIENT_SIM.stop()
			return False

	@staticmethod
	def run_app():
		"""
		Start the Flask app. This is a blocking method which only returns once the app exists.
		"""

		FLASK_APP.run(host='0.0.0.0', port=5001, debug=True)

	@staticmethod
	def stop():
		"""
		Stops the app and cleans up any threaded code
		"""

		for item in TIMERS:
			item.stop()
