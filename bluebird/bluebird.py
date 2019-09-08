"""
Contains the BlueBird class
"""

import logging
import os
import signal
import threading
import time

from . import settings
from .api import FLASK_APP
from .cache import AC_DATA, SIM_STATE
from .client import CLIENT_SIM
from .metrics import setup_metrics
from . import sectors
from .sectors.utils import check_active_sector, create_bluesky_areas, create_bluesky_waypoints, SectorWatcher
from .utils import TIMERS, check_timers


class BlueBird:
	"""
	The BlueBird API client.
	"""

	exit_flag: bool = False

	def __init__(self):
		self._logger = logging.getLogger(__name__)
		self._logger.info(f'BlueBird init. {settings.SIM_MODE} mode')

		setup_metrics()
		if check_active_sector():
			sectors.WATCHER = SectorWatcher()

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
		BlueBird.exit_flag = True

	def client_connect(self, min_bs_version, reset_on_connect):
		"""
		Connect to the (BlueSky) simulation client
		:return: True if a connection was established with the client, false otherwise.
		"""

		CLIENT_SIM.start()

		self._logger.info('Connecting to client...')

		try:
			CLIENT_SIM.connect(hostname=settings.BS_HOST, event_port=settings.BS_EVENT_PORT,
			                   stream_port=settings.BS_STREAM_PORT, timeout=1)
		except TimeoutError:
			self._logger.error(f'Failed to connect to BlueSky server at {settings.BS_HOST}, exiting')
			return False

		if CLIENT_SIM.host_version < min_bs_version:
			self._logger.error(
							f'BlueSky server of version {CLIENT_SIM.host_version} does not meet the minimum '
							f'requirement ({min_bs_version})')
			return False
		if CLIENT_SIM.host_version.major > min_bs_version.major:
			self._logger.error(
							f'BlueSky server of version {CLIENT_SIM.host_version} has major version greater '
							f'than supported in this version of client ({min_bs_version})')
			return False

		if reset_on_connect:
			CLIENT_SIM.reset_sim()

		# Only (re-)draw sectors and waypoints if we are instance 0
		if settings.SECTOR_IDX == 0:
			create_bluesky_areas()
			create_bluesky_waypoints()

		SIM_STATE.start()
		return True

	def run(self):
		"""
		Start the Flask app. This is a blocking method which only returns once the app exists.
		"""

		self._logger.debug("Starting Flask app")

		AC_DATA.start()

		if sectors.WATCHER:
			sectors.WATCHER.start()

		flask_thread = threading.Thread(target=FLASK_APP.run, kwargs={"host": settings.BB_HOST,
		"port": settings.BB_PORT, "debug": settings.FLASK_DEBUG, "use_reloader": False})

		flask_thread.start()

		try:
			while flask_thread.isAlive() and not check_timers():
				time.sleep(0.1)
		except KeyboardInterrupt:
			self._logger.info('Ctrl+C - exiting')
			_proc_killer()
			return

		err = check_timers()
		if err:
			exc_type, exc_value, exc_traceback = err
			_proc_killer()
			raise exc_type(exc_value).with_traceback(exc_traceback)


def _proc_killer():
	"""
	Starts another thread which waits for BlueBird.exit_flag to be set, then sends
	SIGINT to our own process. This is apparently the easiest way to clean things up and
	cause the Flask server to exit if you decide to run it in another thread ¯\_(ツ)_/¯
	"""

	def killer():
		while not BlueBird.exit_flag:
			time.sleep(0.1)
		os.kill(os.getpid(), signal.SIGINT)

	thread = threading.Thread(target=killer)
	thread.start()
