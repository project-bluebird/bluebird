"""
Basic aircraft separation metric. Specification is:

Let's denote:

- d_h := absolute horizontal distance between the two aircraft (either geodesic or great circle
separation will do) measured in nautical miles (nm)
- d_v := absolute vertical separation between the two aircraft measured in feet (ft)

The simple metric *m* I have in mind is the function of d_h and d_v defined by:

- m(d_h, d_v) = 0, if d_h >= C_h (for any d_v)
- m(d_h, d_v) = 0, if d_v >= C_v (for any d_h)
- m(d_h, d_v) = -1, if d_h < c_h and d_v < c_v (loss of separation)
- m(d_h, d_v) = max{ (d_h - c_h)/(C_h - c_h) - 1, (d_v - c_v)/(C_v - c_v) - 1 }, otherwise

where:

- The c_h (horizontal) and c_v (vertical) thresholds are part of the definition of "loss of
separation", i.e. they're given constants: c_h = 5 nm, c_v = 1000 ft
- The C_h and C_v thresholds are arbitrary parameters (except for the requirement that C_h > c_h
and C_v > c_v), so the function should take them as arguments. Default values could be double the
corresponding lower thresholds, that is: C_h = 10 nm, C_v = 2000 ft
"""

import numpy as np
from pyproj import Geod

from bluebird.cache import AC_DATA
from bluebird.utils.strings import is_acid
from bluebird.sectors.utils import point_inside_sector

from . import config as cfg

_WGS84 = Geod(ellps='WGS84')

_ONE_NM = 1852  # Meters

_SCALE_METRES_TO_FEET = 3.280839895


def _get_pos(acid):
	assert isinstance(acid, str), 'Expected the input to be a string'
	assert is_acid(acid), f'Expected the input to be a valid ACID (given {acid})'
	assert AC_DATA.contains(acid), \
		f'Expected the aircraft \'{acid}\' to exist in the simulation'
	return AC_DATA.get(acid)[acid]


def _vertical_separation(alt1_ft, alt2_ft):
	"""
	Basic vertical separation metric
	:param alt1:
	:param alt2:
	:return:
	"""

	vertical_sep_ft = abs(alt1_ft - alt2_ft)

	if vertical_sep_ft < cfg.VERT_MIN_DIST:
		return cfg.LOS_SCORE

	if vertical_sep_ft < cfg.VERT_WARN_DIST:
		# Linear score between the minimum and warning distances
		return np.interp(vertical_sep_ft,
		                 [cfg.VERT_MIN_DIST, cfg.VERT_WARN_DIST], [cfg.LOS_SCORE, 0])

	return 0


def _horizontal_separation(pos1, pos2):
	"""
	Basic horizontal separation metric
	:param pos1:
	:param pos2:
	:return:
	"""

	_, _, horizontal_sep_m = _WGS84.inv(pos1['lon'], pos1['lat'], pos2['lon'], pos2['lat'])
	horizontal_sep_nm = round(horizontal_sep_m / _ONE_NM)

	if horizontal_sep_nm < cfg.HOR_MIN_DIST:
		return round(cfg.LOS_SCORE, 1)

	if horizontal_sep_nm < cfg.HOR_WARN_DIST:
		# Linear score between the minimum and warning distances
		return round(np.interp(horizontal_sep_nm,
		                       [cfg.HOR_MIN_DIST, cfg.HOR_WARN_DIST], [cfg.LOS_SCORE, 0]), 1)

	return 0


def aircraft_separation(acid1, acid2):
	"""
	Combined score based on horizontal and vertical separation.
	:param acid1:
	:param acid2:
	:return:
	"""

	pos1 = _get_pos(acid1)
	pos2 = _get_pos(acid2)

	ac1_inside = point_inside_sector(pos1)
	ac2_inside = point_inside_sector(pos2)
	if not ac1_inside and not ac2_inside:
		return 'Both the requested aircraft are outside the active sector'

	horizontal_sep = _horizontal_separation(pos1, pos2)

	alt1_ft = pos1['alt'] * _SCALE_METRES_TO_FEET
	alt2_ft = pos2['alt'] * _SCALE_METRES_TO_FEET
	vertical_sep = _vertical_separation(alt1_ft, alt2_ft)

	return max(horizontal_sep, vertical_sep)


### Sector exit metric ###

import logging
import bluebird.sectors as bb_sectors
from bluebird.sectors.utils import SectorWatcher

_LOGGER = logging.getLogger(__name__)

def _get_watcher() -> SectorWatcher:
	if bb_sectors.WATCHER:
		return bb_sectors.WATCHER
	raise ValueError('Sectors are not being monitored')

# Constants
c_h = 0
C_h = 0
c_v = 0
C_v = 0

def sector_exit_impl(target_exit, actual_exit):
	
	def v(d, c, C):
		assert c < C, 'Expected ...'
		if d < c:
			return 0
		if d > C:
			return 1
		return -(d-c)/(C-c)

	_, _, horizontal_sep_m = _WGS84.inv(target_exit['lon'], target_exit['lat'], \
		actual_exit['lon'], actual_exit['lat'])
	v_h = v(horizontal_sep_m, c_h, C_h)

	vertical_sep_m = abs(target_exit['alt'] - actual_exit['alt'])
	v_v = v(vertical_sep_m, c_v, C_v)

	return min(v_h, v_v)


def sector_exit(acid):
	"""
	Metric score based on the aircraft's exit point from the sector
	:param acid1:
	"""

	# Don't necessarily want to check AC_DATA - BlueSky may have already deleted the
	# aircraft if it has travelled outside the experiment area
	assert isinstance(acid, str), 'Expected the input to be a string'
	assert is_acid(acid), f'Expected the input to be a valid ACID (given {acid})'

	exit_loc = _get_watcher().check_exited(acid)

	if isinstance(exit_loc, str):
		return exit_loc

	# We have the sector exit position!
	_LOGGER.info(f'Aircraft {acid} exited at {exit_loc}')

	# TODO Need to calculate what this should be from the aircraft's route
	target_exit_loc = None

	return sector_exit_impl(target_exit_loc, exit_loc)
