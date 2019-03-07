"""
Contains the class for storing aircraft data which is streamed from the simulation
"""

import json

import datetime

import bluebird.cache
import bluebird.logging
from bluebird.settings import SIM_LOG_FREQ
from bluebird.utils import TIMERS, Timer
from .base import Cache, generate_extras

LOG_PREFIX = 'A'


# Note on unit precision:
#   lat/lon 5 d.p. is ~1.1 meters, so can round to 5 places
#   gs      1 knot is ~0.5 m/s, so can store as an int
#   vs      1 fpm  is ~0.005 m/s, so can store as an int


class AcDataCache(Cache):
	"""
	Holds the most recent aircraft data
	"""

	def __init__(self):
		super().__init__()

		# Periodically log the sim state to file. Starts disabled.
		self.timer = Timer(self._log, SIM_LOG_FREQ)
		self.timer.disabled = True

	def start(self):
		self.timer.start()
		TIMERS.append(self.timer)

	def get(self, key):
		"""
		Get data for an aircraft
		:param key: An aircraft identifier
		:return: Aircraft information
		"""

		acid = key.upper()

		# If requested, just return the complete aircraft data
		if acid == 'ALL':
			return self.store

		return super().get(acid)

	def fill(self, data):

		if isinstance(data, dict) and 'id' in data:

			for idx in range(len(data['id'])):
				acid = data['id'][idx]
				ac_data = {'alt': int(data['alt'][idx]), 'lat': round(data['lat'][idx], 5),
				           'lon': round(data['lon'][idx], 5), 'gs': int(data['gs'][idx]),
				           'vs': int(data['vs'][idx])}

				self.store[acid] = {**ac_data, **generate_extras()}

	def _log(self):

		if not self.store:
			return

		# TODO Tidy this up
		data = dict(self.store)
		for ac in data.keys():
			for k in list(data[ac].keys()):
				if k.startswith('_'):
					del data[ac][k]
					continue
				if isinstance(data[ac][k], datetime.datetime):
					data[ac][k] = str(data[ac][k].utcnow())

		sim_t = bluebird.cache.SIM_STATE.sim_t
		json_data = json.dumps(data, separators=(',', ':'))
		bluebird.logging.EP_LOGGER.debug(f'[{sim_t}] {json_data}', extra={'PREFIX': LOG_PREFIX})
