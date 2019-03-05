"""
Logging configuration for BlueBird
"""

import json
import logging.config
import os

from datetime import datetime

if not os.path.exists('logs'):
	os.mkdir('logs')

with open('bluebird/logging_config.json') as f:
	LOG_CONFIG = json.load(f)

# Set filenames for logfiles (can't do this from the JSON)
LOG_TIME = datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
LOG_CONFIG['handlers']['debug-file']['filename'] = f'logs/{LOG_TIME}-debug.log'
LOG_CONFIG['handlers']['episode-file']['filename'] = f'logs/{LOG_TIME}-episode.log'

# Set the logging config
logging.config.dictConfig(LOG_CONFIG)
