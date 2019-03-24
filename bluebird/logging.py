"""
Logging configuration for BlueBird
"""

import json
import logging.config
import os

from datetime import datetime


# TODO Cli option - single episode log

def log_name_time():
	"""
	Returns the current formatted timestamp
	:return:
	"""
	return datetime.now().strftime('%Y-%m-%d-%H-%M-%S')


if not os.path.exists('logs'):
	os.mkdir('logs')

with open('bluebird/logging_config.json') as f:
	LOG_CONFIG = json.load(f)

# Set filenames for logfiles (can't do this from the JSON)
LOG_CONFIG['handlers']['debug-file']['filename'] = f'logs/{log_name_time()}-debug.log'

# Set the logging config
logging.config.dictConfig(LOG_CONFIG)

# Setup episode logging

EP_LOGGER = logging.getLogger('episode')
EP_LOGGER.setLevel(logging.DEBUG)

_LOG_PREFIX = 'E'


# TODO: Remove this when we move away from loading files
def bodge_file_content(filename):
	"""
	Log the content of the scenario file which was loaded.	Interim solution until we move away from
	using BlueSky's default scenario files...
	:param filename:
	:return:
	"""

	EP_LOGGER.info(f"Scenario file loaded: {filename}", extra={'PREFIX': _LOG_PREFIX})
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

	if EP_LOGGER.hasHandlers():
		raise Exception(f'Episode logger already has a handler assigned: {EP_LOGGER.handlers}')

	file_handler = logging.FileHandler(f'logs/{log_name_time()}-episode.log')
	file_handler.name = 'episode-file'
	file_handler.setLevel(logging.DEBUG)
	formatter = logging.Formatter('%(asctime)s %(PREFIX)s %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
	file_handler.setFormatter(formatter)
	EP_LOGGER.addHandler(file_handler)
	EP_LOGGER.info("Episode started", extra={'PREFIX': _LOG_PREFIX})


def restart_episode_log():
	"""
	Closes the current episode log and starts a new one
	:return:
	"""

	close_episode_log('episode logging restarted')
	_start_episode_log()
