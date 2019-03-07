"""
Module contains logic for storing the state of the remote simulation
"""

import logging

import bluebird.cache
from bluebird.settings import SIM_LOG_FREQ
from bluebird.utils import TIMERS, Timer

# Note - BlueSky SIMINFO returns:
# [speed, bs.sim.simdt, bs.sim.simt, str(bs.sim.utc.replace(microsecond=0)), bs.traf.ntraf,
# bs.sim.state, stack.get_scenname()]
# [1.0015915889597933, 0.05, 3550.1500000041497, '2019-03-06 00:59:10', 2, 2, '']

# BlueSky simulation states (OP renamed to RUN)
BS_STATES = ['INIT', 'HOLD', 'RUN', 'END']


class SimState:
	"""
	Proxy class for the simulation state
	"""

	def __init__(self):
		self.logger = logging.getLogger(__name__)
		self.timer = Timer(self._log, 1 / 5)

		self.sim_speed = 0
		self.sim_dt = 0
		self.sim_t = 0
		self.sim_state = 0
		self.ac_count = 0
		self.scn_name = ''

	def start(self):
		self.timer.start()
		TIMERS.append(self.timer)

	def update(self, data):
		old_speed = self.sim_speed
		self.sim_speed, self.sim_dt, self.sim_t, _, self.ac_count, self.sim_state, self.scn_name = data
		self.sim_speed = round(self.sim_speed, 1)
		self.sim_t = round(self.sim_t)

		if self.sim_speed > 0 and old_speed == 0:
			self.logger.info('Simulation resumed')
			rate = round(1 / self.sim_speed, 2) / SIM_LOG_FREQ
			self.logger.info(f'New log time: {rate}')
			bluebird.cache.AC_DATA.timer.set_tickrate(rate)
			bluebird.cache.AC_DATA.timer.disabled = False
			return

		if self.sim_speed == 0 and old_speed != 0:
			self.logger.info('Simulation paused')
			bluebird.cache.AC_DATA.timer.disabled = True
			return

		if (old_speed != self.sim_speed) and not bluebird.cache.AC_DATA.is_empty():
			self.logger.info(f'Sim speed changed: {old_speed}x -> {self.sim_speed}x')
			rate = round(1 / self.sim_speed, 2) / SIM_LOG_FREQ
			self.logger.info(f'New log time: {rate}')
			bluebird.cache.AC_DATA.timer.set_tickrate(rate)
			bluebird.cache.AC_DATA.timer.disabled = False

	def _log(self):
		data = f'SIM :: speed={self.sim_speed}x, time={self.sim_t},' \
		       f'state={BS_STATES[self.sim_state]}, aircraft={self.ac_count}'
		self.logger.info(data)
