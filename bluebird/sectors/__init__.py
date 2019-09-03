"""
BlueBird sectors package
"""

import logging

from bluebird import settings


_LOGGER = logging.getLogger(__name__)


def set_active_sector():

	idx = settings.SECTOR_IDX
	if idx == -1:
		_LOGGER.info(f'BB_SECTOR_IDX not set. All defined sectors will be monitored')
		return

	if idx >= len(settings.SECTORS):
		raise ValueError(f'BB_SECTOR_IDX is larger than the number of defined sectors')

	_LOGGER.info(f'Monitoring BB_SECTOR_IDX={idx}')
