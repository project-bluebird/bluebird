"""
Contains the BlueSky client class for our API
"""

import json
import logging
import time

import msgpack
import zmq

import bluebird.cache as bb_cache
import bluebird.logging
import bluebird.utils as bb_utils
from bluebird.utils import Timer
from bluebird.utils.timeutils import timeit
from bluesky.network.client import Client
from bluesky.network.npcodec import decode_ndarray

CMD_LOG_PREFIX = 'C'

# The BlueSky streams we subscribe to. 'ROUTEDATA' is also available
ACTIVE_NODE_TOPICS = [b'ACDATA', b'SIMINFO']

# Same rate as GuiClient polls for its data
POLL_RATE = 50  # Hz

# Events which should be ignored
IGNORED_EVENTS = [b'DEFWPT', b'DISPLAYFLAG', b'PANZOOM', b'SHAPE']

# Tuple of strings which should not be considered error responses from BlueSky
IGNORED_RESPONSES = ('TIME', 'DEFWPT', 'AREA', 'BlueSky Console Window')


class ApiClient(Client):
	"""
	Client class for the BlueSky simulator
	"""

	def __init__(self):
		super(ApiClient, self).__init__(ACTIVE_NODE_TOPICS)

		self._logger = logging.getLogger(__name__)

		# Continually poll for the sim state
		self.timer = Timer(self.receive, POLL_RATE)

		self.seed = None
		self.step_dt = 1

		self._reset_flag = False
		self._step_flag = False
		self._echo_data = []
		self._scn_response = None
		self._awaiting_exit_resp = False

	def start(self):
		"""
		Start the client
		:return:
		"""

		self.timer.start()
		bb_utils.TIMERS.append(self.timer)

	def stop(self):
		"""
		Stop the client and disconnect
		"""

		self.timer.stop()
		bluebird.logging.close_episode_log('client was stopped')

	def stream(self, name, data, sender_id):
		"""
		Method called to process data received on a stream
		:param name:
		:param data:
		:param sender_id:
		"""

		# Fill the cache with the aircraft data
		if name == b'ACDATA':
			bb_cache.AC_DATA.fill(data)

		elif name == b'SIMINFO':
			bb_cache.SIM_STATE.update(data)

		self.stream_received.emit(name, data, sender_id)

	def send_stack_cmd(self, data=None, response_expected=False, target=b'*'):
		"""
		Send a command to the BlueSky simulation command stack
		:param data:
		:param response_expected:
		:param target:
		"""

		sim_t = bb_cache.SIM_STATE.sim_t
		bluebird.logging.EP_LOGGER.debug(f'[{sim_t}] {data}', extra={'PREFIX': CMD_LOG_PREFIX})

		self._echo_data = []
		self.send_event(b'STACKCMD', data, target)

		time.sleep(25 / POLL_RATE)

		if response_expected and self._echo_data:
			return list(self._echo_data)

		if self._echo_data:

			if self._echo_data[0].startswith(IGNORED_RESPONSES):
				return None

			self._logger.error(f'Command \'{data}\' resulted in error: {self._echo_data}')
			errs = '\n'.join(str(x) for x in self._echo_data)
			return str(f'Error(s): {errs}')

		if response_expected:
			return 'Error: no response received'

		return None

	def receive(self, timeout=0):
		try:
			socks = dict(self.poller.poll(timeout))
			if socks.get(self.event_io) == zmq.POLLIN:

				msg = self.event_io.recv_multipart()

				# Remove send-to-all flag if present
				if msg[0] == b'*':
					msg.pop(0)

				route, eventname, data = msg[:-2], msg[-2], msg[-1]

				self.sender_id = route[0]
				route.reverse()
				pydata = msgpack.unpackb(data, object_hook=decode_ndarray,
				                         encoding='utf-8') if data else None

				self._logger.debug('EVT :: {} :: {}'.format(eventname, pydata))

				if eventname in IGNORED_EVENTS:
					self._logger.debug(f'Ignored event {eventname}')

				# TODO Is this case relevant here?
				elif eventname == b'NODESCHANGED':
					self.servers.update(pydata)
					self.nodes_changed.emit(pydata)

					# If this is the first known node, select it as active node
					nodes_myserver = next(iter(pydata.values())).get('nodes')
					if not self.act and nodes_myserver:
						self.actnode(nodes_myserver[0])

				# TODO Also check the pydata contains 'syntax error' etc.
				elif eventname == b'ECHO':
					text = pydata['text']
					if text.startswith('Unknown command: METRICS'):
						self._logger.warning('Ignored warning about invalid "METRICS" command')
					elif not text.startswith('IC: Opened'):
						self._echo_data.append(text)

				elif eventname == b'STEP':
					self._step_flag = True

				elif eventname == b'RESET':
					self._reset_flag = True
					self._logger.info('Received BlueSky simulation reset message')

				elif eventname == b'QUIT':
					if self._awaiting_exit_resp:
						self._awaiting_exit_resp = False
					else:
						self._logger.error('Unhandled quit event from simulation')

				elif eventname == b'SCENARIO':
					self._scn_response = pydata

				else:
					self._logger.warning('Unhandled eventname "{} with data {}"'.format(eventname, pydata))
					self.event(eventname, pydata, self.sender_id)

			if socks.get(self.stream_in) == zmq.POLLIN:
				msg = self.stream_in.recv_multipart()

				strmname = msg[0][:-5]
				sender_id = msg[0][-5:]
				pydata = msgpack.unpackb(msg[1], object_hook=decode_ndarray, encoding='utf-8')

				self.stream(strmname, pydata, sender_id)

			return True

		except zmq.ZMQError as exc:
			self._logger.error(exc)
			return False

	@timeit('Client')
	def upload_new_scenario(self, name, lines):
		"""
		Uploads a new scenario file to the BlueSky simulation
		:param name:
		:param lines:
		:return:
		"""

		self._scn_response = None

		data = json.dumps({'name': name, 'lines': lines})
		self.send_event(b'SCENARIO', data)

		time.sleep(25 / POLL_RATE)
		resp = self._scn_response

		if not resp == 'Ok':
			return resp if resp else 'No response received'
		return None

	def load_scenario(self, filename, speed=1.0, start_paused=False):
		"""
		Load a scenario from a file
		:param speed:
		:param filename:
		:param start_paused:
		:return:
		"""

		bb_cache.AC_DATA.reset()
		episode_id = bluebird.logging.restart_episode_log(self.seed)
		self._logger.info(f'Episode {episode_id} started. Speed {speed}')
		bb_cache.AC_DATA.set_log_rate(speed, new_log=True)

		self._reset_flag = False

		err = self.send_stack_cmd('IC ' + filename)
		if err:
			return err

		err = self._await_reset_confirmation()
		if err:
			return err

		if start_paused:
			err = self.send_stack_cmd('HOLD')
			if err:
				return err

		bluebird.logging.bodge_file_content(filename)

		if speed != 1.0:
			cmd = f'DTMULT {speed}'
			err = self.send_stack_cmd(cmd)
			if err:
				return err

		return None

	def step(self):
		"""
		Steps the simulation forward
		:return:
		"""

		init_t = bluebird.cache.SIM_STATE.sim_t
		bluebird.logging.EP_LOGGER.debug(f'[{init_t}] STEP', extra={'PREFIX': CMD_LOG_PREFIX})

		self._step_flag = False
		self.send_event(b'STEP')

		# Wait for the STEP response, and for the sim_t to have advanced
		wait_t = 1 / POLL_RATE
		total_t = 0
		while not self._step_flag and (bluebird.cache.SIM_STATE.sim_t == init_t):
			time.sleep(wait_t)
			total_t += wait_t
			if total_t >= 5:
				return f'Error: Could not step. step_flag={self._step_flag} ' \
				       f'sim_t={bluebird.cache.SIM_STATE.sim_t}'

		return None

	def reset_sim(self):
		"""
		Resets the BlueSky sim and handles the response
		:return:
		"""

		bb_cache.AC_DATA.timer.disabled = True
		bluebird.logging.close_episode_log('sim reset')

		self._reset_flag = False
		err = self.send_stack_cmd('RESET')

		return err if err else self._await_reset_confirmation()

	def _await_reset_confirmation(self):
		"""
		Waits for reset_flag to be set, then clears AC_DATA.
		:return: True if the simulation was reset
		"""

		time.sleep(25 / POLL_RATE)
		if not self._reset_flag:
			return 'Did not receive reset confirmation in time!'

		bb_cache.AC_DATA.clear()
		return None

	def quit(self):
		"""
		Sends a shutdown message to the simulation server
		:return:
		"""

		self._awaiting_exit_resp = True
		self.send_event(b'QUIT', target=b'*')
		time.sleep(25 / POLL_RATE)
		return not bool(self._awaiting_exit_resp)
