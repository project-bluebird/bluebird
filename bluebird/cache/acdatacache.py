"""
Contains the class for storing aircraft data which is streamed from the simulation
"""

import json
import logging

import datetime

import bluebird.cache
import bluebird.logging
from bluebird.settings import SIM_LOG_RATE
from bluebird.utils import TIMERS, Timer
from bluebird.utils.timeutils import log_rate
from .base import Cache

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

		self._logger = logging.getLogger(__name__)

		# Periodically log the sim state to file. Starts disabled.
		self.timer = Timer(self._log, SIM_LOG_RATE)
		self.timer.disabled = True

	def start(self):
		"""
		Starts the timer for logging
		:return:
		"""

		self.timer.start()
		TIMERS.append(self.timer)

	def get(self, key):
		"""
		Get data for an aircraft
		:param key: An aircraft identifier
		:return: Aircraft information
		"""

		query = key.upper()

		if query == 'ALL':
			data = dict(self.store)
		else:
			data = {}
			for acid in filter(None, query.split(',')):
				data[acid] = super().get(acid)

		if data is not None:
			sim_state = bluebird.cache.SIM_STATE
			data['sim_t'] = sim_state.sim_t

		return data

	def contains(self, acid):
		"""
		Check if the given acid exists in the simulation
		:param acid:
		:return:
		"""
		return acid in self.store.keys()

	def fill(self, data):

		if isinstance(data, dict) and 'id' in data:

			for idx in range(len(data['id'])):
				acid = data['id'][idx]
				ac_data = {'actype': data['actype'][idx], 'alt': int(data['alt'][idx]),
				           'lat': round(data['lat'][idx], 5), 'lon': round(data['lon'][idx], 5),
				           'gs': int(data['gs'][idx]), 'vs': int(data['vs'][idx])}

				self.store[acid] = ac_data

	def set_log_rate(self, new_speed, new_log=False):
		"""
		Set the speed at which simulation data is logged at
		:param new_log:
		:param new_speed:
		:return:
		"""

		sim_state = bluebird.cache.SIM_STATE
		current_speed = sim_state.sim_speed

		rate = log_rate(new_speed)

		if new_log or (new_speed > 0 and current_speed == 0):
			state = 'started' if new_log else 'resumed'
			self._logger.info(f'Simulation {state}. Log rate: {rate}')
			self.timer.set_tickrate(rate)
			self.timer.disabled = False
			return

		if new_speed == 0 and current_speed != 0:
			self._logger.info('Simulation paused')
			self.timer.disabled = True
			return

		if current_speed != new_speed:
			self._logger.info(f'Sim speed changed: {current_speed}x -> {new_speed}x. New '
			                  f'log rate: {rate}')
			self.timer.set_tickrate(rate)
			return

	def _log(self):

		if not self.store:
			return

		# TODO Tidy this up
		data = dict(self.store)
		for aircraft in data.keys():  # pylint: disable=consider-iterating-dictionary
			for prop in list(data[aircraft].keys()):
				if prop.startswith('_'):
					del data[aircraft][prop]
					continue
				if isinstance(data[aircraft][prop], datetime.datetime):
					data[aircraft][prop] = str(data[aircraft][prop].utcnow())

		sim_t = bluebird.cache.SIM_STATE.sim_t
		json_data = json.dumps(data, separators=(',', ':'))
		bluebird.logging.EP_LOGGER.debug(f'[{sim_t}] {json_data}', extra={'PREFIX': LOG_PREFIX})
