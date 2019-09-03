"""
Utility functions for the sector package
"""

import logging

import bluebird.client as bb_client
import bluebird.settings as settings


_SCALE_METRES_TO_FEET = 3.280839895

_LOGGER = logging.getLogger(__name__)


def set_active_sector():

	idx = settings.SECTOR_IDX
	if idx == -1:
		_LOGGER.info(f'BB_SECTOR_IDX not set. All defined sectors will be monitored')
		return

	if idx >= len(settings.SECTORS):
		raise ValueError(f'BB_SECTOR_IDX is larger than the number of defined sectors')

	_LOGGER.info(f'Monitoring BB_SECTOR_IDX={idx}')


def create_bluesky_areas():
	for sector in settings.SECTORS:
		cmd_str = f"BOX {sector['name']} {sector['min_lat']} {sector['min_lon']} " \
			f"{sector['max_lat']} {sector['max_lon']} {sector['max_alt']} {sector['min_alt']}"
		_LOGGER.info(cmd_str)
		err = bb_client.CLIENT_SIM.send_stack_cmd(cmd_str)
		if err:
			raise RuntimeError(err)


def point_inside_sector(point) -> bool:
	"""
	Checks if a point (lat, lon, alt) is inside the current active sector
	"""

	# Don't care about sectors in this case, so every point is inside the global sector
	if settings.SECTOR_IDX == -1:
		return True

	sector = settings.SECTORS[settings.SECTOR_IDX]
	alt = point['alt']  * _SCALE_METRES_TO_FEET

	return \
		((sector['min_lat'] <= point['lat']) and (point['lat'] <= sector['max_lat'])) and \
		((sector['min_lon'] <= point['lon']) and (point['lon'] <= sector['max_lon'])) and \
		((sector['min_alt'] <= alt) and (alt <= sector['max_alt']))
