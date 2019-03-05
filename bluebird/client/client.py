"""
Contains the BlueSky client class for our API
"""

import logging
import time

import msgpack
import zmq

from bluebird.cache import AC_DATA
from bluebird.utils import TIMERS, Timer
from bluesky.network.client import Client
from bluesky.network.npcodec import decode_ndarray

LOG_PREFIX = 'E'

# TODO Figure out what we topics we need to subscribe to. Is there a list of possible events?
ACTIVE_NODE_TOPICS = [b'ACDATA', b'SIMINFO']  # Also available: ROUTEDATA

# Same rate as GuiClient polls for its data
POLL_RATE = 50  # Hz


class ApiClient(Client):
	"""
	Client class for the BlueSky simulator
	"""

	def __init__(self):
		super(ApiClient, self).__init__(ACTIVE_NODE_TOPICS)

		self._logger = logging.getLogger(__name__)
		self._ep_logger = logging.getLogger('episode')

		self.recording = False

		# Continually poll for the sim state
		self.timer = Timer(self.receive, int(1 / POLL_RATE))

		self.reset_flag = False
		self.echo_data = None

	def start(self):
		"""
		Start the client
		:return:
		"""

		self.timer.start()
		TIMERS.append(self.timer)

	def stop(self):
		"""
		Stop the client and disconnect
		"""

		self.timer.stop()

	def stream(self, name, data, sender_id):
		"""
		Method called to process data received on a stream
		:param name:
		:param data:
		:param sender_id:
		"""

		# Fill the cache with the aircraft data
		if name == b'ACDATA':
			AC_DATA.fill(data)

		elif name == b'SIMINFO':
			# TODO Figure out what data is provided here
			self._logger.info('SIMINFO {}'.format(data))

		self.stream_received.emit(name, data, sender_id)

	def send_stack_cmd(self, data=None, target=b'*'):
		"""
		Send a command to the BlueSky simulation command stack
		:param data:
		:param target:
		"""

		self.echo_data = None
		self.send_event(b'STACKCMD', data, target)

		time.sleep(25 / POLL_RATE)

		if self.echo_data:
			self._logger.error(f'Command \'{data}\' resulted in error: {self.echo_data}')
			return self.echo_data['text']

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
						self.echo_data = pydata

				# TODO Also handle the following message which asserts the scenario was loaded:
				# b'ECHO', {'text': 'IC: Opened IC', 'flags': 0}
				elif eventname == b'RESET':
					self._logger.info('Received BlueSky simulation reset message')
					self.reset_flag = True

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

			# If we are in discovery mode, parse this message
			if self.discovery and socks.get(self.discovery.handle.fileno()):
				dmsg = self.discovery.recv_reqreply()
				if dmsg.conn_id != self.client_id and dmsg.is_server:
					self.server_discovered.emit(dmsg.conn_ip, dmsg.ports)

			return True

		except zmq.ZMQError as exc:
			self._logger.error(exc)
			return False

	def load_scenario(self, filename):
		"""
		Load a scenario from a file
		:param filename:
		:return:
		"""

		self.reset_flag = False

		err = self.send_stack_cmd('IC ' + filename)
		return err if err else self._await_reset_confirmation()

	def reset_sim(self):
		"""
		Resets the BlueSky sim and handles the response
		:return:
		"""

		self.reset_flag = False

		err = self.send_stack_cmd('RESET')
		return err if err else self._await_reset_confirmation()

	def _await_reset_confirmation(self):
		"""
		Waits for reset_flag to be set, then clears AC_DATA.
		:return: True if the simulation was reset
		"""

		time.sleep(25 / POLL_RATE)
		if not self.reset_flag:
			self._logger.error('Did not receive reset confirmation in time!')
			return False

		AC_DATA.clear()
		self._ep_logger.info("Episode started", extra={'PREFIX': LOG_PREFIX})
		self.recording = True
