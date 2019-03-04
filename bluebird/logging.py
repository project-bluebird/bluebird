"""
Logging configuration for BlueBird
"""

import json
import logging.config
import logging.handlers
import os

from datetime import datetime

LOG_TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')

if not os.path.exists('logs'):
	os.mkdir('logs')

with open('bluebird/logging_config.json') as f:
	LOG_CONFIG = json.load(f)
	LOG_CONFIG['handlers']['debug-file']['filename'] = f'logs/{LOG_TIME}-debug.log'

	logging.config.dictConfig(LOG_CONFIG)
