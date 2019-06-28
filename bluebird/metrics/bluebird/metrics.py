"""
(Very) basic evaluation metrics
"""

import numpy as np
from pyproj import Geod

from bluebird.cache import AC_DATA
from bluebird.utils.strings import is_acid
from . import config as cfg

_WGS84 = Geod(ellps='WGS84')


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
	vertical_sep = abs(alt1 - alt2)

	if vertical_sep < cfg.VERT_MIN:
		return cfg.VERT_SCORE

	if vertical_sep < cfg.VERT_WARN:
		# Linear score between the minimum and warning distances
		return np.interp(vertical_sep, [cfg.VERT_MIN, cfg.VERT_WARN], [cfg.VERT_SCORE, 0])

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

	horizontal_sep_nm = horizontal_sep_m / 1852

	if horizontal_sep_nm < cfg.HOR_MIN:
		return cfg.HOR_SCORE

	if horizontal_sep_nm < cfg.HOR_WARN:
		# Linear score between the minimum and warning distances
		return np.interp(horizontal_sep_nm, [cfg.HOR_MIN, cfg.HOR_WARN], [cfg.HOR_SCORE, 0])

	return 0
