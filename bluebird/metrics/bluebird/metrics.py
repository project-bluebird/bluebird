"""
(Very) basic evaluation metrics
"""

import numpy as np
from pyproj import Geod

from bluebird.cache import AC_DATA
from bluebird.utils.strings import is_acid
from . import config as cfg

_WGS84 = Geod(ellps='WGS84')

_ONE_NM = 1852  # Meters

_SCALE_METRES_TO_FEET = 3.280839895

def _get_pos(acid):
	assert isinstance(acid, str), 'Expected the input to be a string'
	assert is_acid(acid), 'Expected the input to be a valid ACID'
	assert AC_DATA.contains(acid), 'Expected the aircraft to exist in the simulation'
	return AC_DATA.get(acid)[acid]


def vertical_separation(acid1, acid2):
	"""
	Basic vertical separation metric
	:param acid1:
	:param acid2:
	:return:
	"""

	alt1 = _get_pos(acid1)['alt']
	alt2 = _get_pos(acid2)['alt']
	vertical_sep_metres = abs(alt1 - alt2)

	vertical_sep = vertical_sep_metres * _SCALE_METRES_TO_FEET

	if vertical_sep < cfg.VERT_MIN_DIST:
		return cfg.VERT_LOS_SCORE

	if vertical_sep < cfg.VERT_WARN_DIST:
		# Linear score between the minimum and warning distances
		return np.interp(vertical_sep,
		                 [cfg.VERT_MIN_DIST, cfg.VERT_WARN_DIST], [cfg.VERT_LOS_SCORE, 0])

	return 0


def horizontal_separation(acid1, acid2):
	"""
	Basic horizontal separation metric
	:param acid1:
	:param acid2:
	:return:
	"""

	pos1 = _get_pos(acid1)
	pos2 = _get_pos(acid2)

	_, _, horizontal_sep_m = _WGS84.inv(pos1['lon'], pos1['lat'], pos2['lon'], pos2['lat'])
	horizontal_sep_nm = round(horizontal_sep_m / _ONE_NM)

	if horizontal_sep_nm < cfg.HOR_MIN_DIST:
		return round(cfg.HOR_LOS_SCORE, 1)

	if horizontal_sep_nm < cfg.HOR_WARN_DIST:
		# Linear score between the minimum and warning distances
		return round(np.interp(horizontal_sep_nm,
		                       [cfg.HOR_MIN_DIST, cfg.HOR_WARN_DIST], [cfg.HOR_LOS_SCORE, 0]), 1)

	return 0
