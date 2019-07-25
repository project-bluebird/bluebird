"""
Default settings for the BlueBird app
"""

import os
from enum import IntEnum

from semver import VersionInfo

# BlueBird app settings

with open('VERSION') as version_file:
	_VERSION_STR = version_file.read().strip()
	VERSION = VersionInfo.parse(_VERSION_STR)

API_VERSION = 1

FLASK_DEBUG = True

BB_HOST = '0.0.0.0'
BB_PORT = 5001

SIM_LOG_RATE = 0.2  # Rate (in sim-seconds) at which aircraft data is logged to the episode file

LOGS_ROOT = os.getenv('BB_LOGS_ROOT', 'logs')
CONSOLE_LOG_LEVEL = 'INFO'  # Change to 'DEBUG' if needed

# List of package names containing metrics providers
METRICS_PROVIDERS = ['bluebird']

# Current modes:
# sandbox - Default. Simulation runs normally
# agent - Simulation starts paused and must be manually advanced with STEP
# TODO Enum-ify this
SIM_MODES = ['sandbox', 'agent']
SIM_MODE = SIM_MODES[0]


# Simulator app settings

class SimType(IntEnum):
	"""
	Supported simulators
	"""

	BlueSky = 1
	MachColl = 2

	@classmethod
	def _missing_(cls, value):
		for member in cls:
			if SimType(member).name.lower() == value.lower():
				return member
		raise ValueError(f'SimType has no value \"{value}\"')


SIM_TYPE = SimType.BlueSky
SIM_HOST = 'localhost'

# BlueSky specific settings

BS_EVENT_PORT = 9000
BS_STREAM_PORT = 9001
