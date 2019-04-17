"""
Logging configuration for BlueBird
"""

# TODO Cli option - single episode log

import json
import logging.config
import os

import uuid
from datetime import datetime

from .settings import LOGS_ROOT, SIM_LOG_RATE

if not os.path.exists(LOGS_ROOT):
	os.mkdir(LOGS_ROOT)


def log_name_time():
	"""
	Returns the current formatted timestamp
	:return:
	"""
	return datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


INSTANCE_ID = uuid.uuid1()
INST_LOG_DIR = os.path.join(LOGS_ROOT, f'{log_name_time()}_{INSTANCE_ID}')
os.mkdir(INST_LOG_DIR)

with open('bluebird/logging_config.json') as f:
	LOG_CONFIG = json.load(f)

# Set filenames for logfiles (can't do this from the JSON)
LOG_CONFIG['handlers']['debug-file']['filename'] = os.path.join(INST_LOG_DIR, 'debug.log')

# Set the logging config
logging.config.dictConfig(LOG_CONFIG)

# Setup episode logging

EP_ID = EP_FILE = None
EP_LOGGER = logging.getLogger('episode')
EP_LOGGER.setLevel(logging.DEBUG)

_LOG_PREFIX = 'E'


# TODO: Remove this when we move away from loading files
def bodge_file_content(filename):
	"""
	Log the content of the scenario file which was loaded.	Interim solution until we move away from
	using BlueSky's default scenario files. Note that we log the contents of our copy of the scenario
	files, so this won't reflect any changes to BlueSky's files (which are actually loaded).
	:param filename:
	:return:
	"""

	EP_LOGGER.info(f"Scenario file loaded: {filename}. Contents are:", extra={'PREFIX': _LOG_PREFIX})
	scn_file = os.path.join('bluesky', filename)

	try:
		with open(scn_file, 'r') as scn:
			for line in scn:
				if line.isspace() or line.strip()[0] == "#":
					continue
				EP_LOGGER.info(line.lstrip().strip('\n'), extra={'PREFIX': _LOG_PREFIX})

	except Exception as exc:  # pylint: disable=broad-except
		EP_LOGGER.error(f'Could not log file contents', exc_info=exc)


def close_episode_log(reason):
	"""
	Closes the currently open episode log, if there is one
	:return:
	"""

	if not EP_LOGGER.hasHandlers():
		return

	EP_LOGGER.info(f'Episode finished ({reason})', extra={'PREFIX': _LOG_PREFIX})
	EP_LOGGER.handlers.pop()


def _start_episode_log():
	"""
	Starts a new episode logfile
	:return:
	"""

	global EP_ID, EP_FILE  # pylint: disable=global-statement

	if EP_LOGGER.hasHandlers():
		raise Exception(f'Episode logger already has a handler assigned: {EP_LOGGER.handlers}')

	EP_ID = uuid.uuid4()
	EP_FILE = os.path.join(INST_LOG_DIR, f'{log_name_time()}_{EP_ID}.log')
	file_handler = logging.FileHandler(EP_FILE)
	file_handler.name = 'episode-file'
	file_handler.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s %(PREFIX)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	file_handler.setFormatter(formatter)
	EP_LOGGER.addHandler(file_handler)
	EP_LOGGER.info(f'Episode started. SIM_LOG_RATE is {SIM_LOG_RATE} Hz', extra={'PREFIX': _LOG_PREFIX})

	return EP_ID


def restart_episode_log():
	"""
	Closes the current episode log and starts a new one. Returns the UUID of the new episode
	:return:
	"""

	close_episode_log('episode logging restarted')
	return _start_episode_log()
