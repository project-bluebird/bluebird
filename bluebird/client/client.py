"""
Contains the BlueSky client class for our API
"""

import logging
import time

import msgpack
import zmq

import bluebird.cache as bb_cache
import bluebird.logging
import bluebird.utils as bb_utils
from bluebird.utils import Timer
from bluesky.network.client import Client
from bluesky.network.npcodec import decode_ndarray

CMD_LOG_PREFIX = 'C'

# The BlueSky streams we subscribe to. 'ROUTEDATA' is also available
ACTIVE_NODE_TOPICS = [b'ACDATA', b'SIMINFO']

# Same rate as GuiClient polls for its data
POLL_RATE = 50  # Hz

# Tuple of strings which should not be considered error responses from BlueSky
ALLOWED_RESPONSES = (' ', '*', 'TIME', 'DEFWPT', 'AREA')


class ApiClient(Client):
	"""
	Client class for the BlueSky simulator
	"""

	def __init__(self):
		super(ApiClient, self).__init__(ACTIVE_NODE_TOPICS)

		self._logger = logging.getLogger(__name__)

		# Continually poll for the sim state
		self.timer = Timer(self.receive, POLL_RATE)

		self._reset_flag = False
		self._echo_data = []

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

		is_error_response = False

		if response_expected and self._echo_data:
			if self._echo_data[0].startswith(ALLOWED_RESPONSES):
				return list(self._echo_data)
			is_error_response = True
		elif self._echo_data:
			is_error_response = True

		if is_error_response:
			self._logger.error(f'Command \'{data}\' resulted in error: {self._echo_data}')
			errs = '\n'.join(str(x) for x in self._echo_data)
			return str(f'Error(s): {errs}')

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
				pydata = msgpack.unpackb(data, object_hook=decode_ndarray, encoding='utf-8')

				self._logger.debug('EVT :: {} :: {}'.format(eventname, pydata))

				# TODO Is this case relevant here?
				if eventname == b'NODESCHANGED':
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

				elif eventname == b'RESET':
					self._reset_flag = True
					self._logger.info('Received BlueSky simulation reset message')

				# TODO Handle simulation exit before client
				elif eventname == b'QUIT':
					self._logger.info('Received sim exit')
					self.signal_quit.emit()

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

	def load_scenario(self, filename, speed=1.0):
		"""
		Load a scenario from a file
		:param speed:
		:param filename:
		:return:
		"""

		bb_cache.AC_DATA.timer.disabled = True
		episode_id = bluebird.logging.restart_episode_log()
		self._logger.info(f'Episode {episode_id} started. Speed {speed}')
		bb_cache.AC_DATA.set_log_rate(speed, new_log=True)

		self._reset_flag = False
		err = self.send_stack_cmd('IC ' + filename, response_expected=True)

		if err:
			# Some scenario files define an area, which is passed back to the client in a message
			if not (isinstance(err, list) and len(err) == 1 and err[0].startswith(ALLOWED_RESPONSES)):
				return err

		err = self._await_reset_confirmation()

		if err:
			return err

		bluebird.logging.bodge_file_content(filename)

		if speed != 1.0:
			cmd = f'DTMULT {speed}'
			err = self.send_stack_cmd(cmd)
			if err:
				return err

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
