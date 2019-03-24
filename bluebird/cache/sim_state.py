"""
Module contains logic for storing the state of the remote simulation
"""

import logging

from bluebird.settings import SIM_LOG_RATE
from bluebird.utils import TIMERS, Timer

# Note - BlueSky SIMINFO returns:
# [speed, bs.sim.simdt, bs.sim.simt, str(bs.sim.utc.replace(microsecond=0)), bs.traf.ntraf,
# bs.sim.state, stack.get_scenname()]
# [1.0015915889597933, 0.05, 3550.1500000041497, '2019-03-06 00:59:10', 2, 2, '']

# BlueSky simulation states (OP renamed to RUN)
BS_STATES = ['INIT', 'HOLD', 'RUN', 'END']


# TODO Sort this with a NamedTuple later
# pylint: disable=too-many-instance-attributes
class SimState:
	"""
	Proxy class for the simulation state
	"""

	def __init__(self):

		self._logger = logging.getLogger(__name__)

		self.timer = Timer(self._log, SIM_LOG_RATE)

		self.sim_speed = 0
		self.sim_dt = 0
		self.sim_t = 0
		self.sim_utc = ''
		self.sim_state = 0
		self.ac_count = 0
		self.scn_name = ''

	def start(self):
		"""
		Starts the timer for logging
		:return:
		"""

		self.timer.start()
		TIMERS.append(self.timer)
		self._logger.info(f'Logging started. Initial SIM_LOG_RATE={SIM_LOG_RATE}')

	def update(self, data):
		"""
		Update the stored simulation state
		:param data:
		:return:
		"""

		self.sim_speed, self.sim_dt, self.sim_t, self.sim_utc, self.ac_count, self.sim_state, \
		self.scn_name = data
		self.sim_speed = round(self.sim_speed, 1)
		self.sim_t = round(self.sim_t)
		self.sim_utc = self.sim_utc.split()[1]

	def _log(self):
		data = f'speed={self.sim_speed}x, ticks={self.sim_t:4}, time={self.sim_utc}, ' \
		       f'state={BS_STATES[self.sim_state]}, aircraft={self.ac_count}'
		self._logger.info(data)
