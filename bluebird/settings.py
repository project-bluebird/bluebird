"""
Default settings for the BlueBird app
"""

import os

from semver import VersionInfo

# BlueBird app settings

with open('VERSION') as version_file:
	version_str = version_file.read().strip()
	VERSION = VersionInfo.parse(version_str)

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
SIM_MODES = ['sandbox', 'agent']
SIM_MODE = SIM_MODES[0]

SECTOR_KEYS = ["name", "min_lat", "max_lat", "min_lon", "max_lon", "min_alt", "max_alt"]
SECTORS = []

# BlueSky server settings

BS_HOST = 'localhost'
BS_EVENT_PORT = 9000
BS_STREAM_PORT = 9001
