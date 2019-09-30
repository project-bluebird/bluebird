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

from bluebird.metrics.bluebird import config as cfg
from bluebird.utils.strings import is_acid

_WGS84 = Geod(ellps="WGS84")

_ONE_NM = 1852  # Meters

_SCALE_METRES_TO_FEET = 3.280839895


def _get_pos(ac_data, acid):
    assert isinstance(acid, str), "Expected the input to be a string"
    assert is_acid(acid), "Expected the input to be a valid ACID"
    assert ac_data.contains(acid), "Expected the aircraft to exist in the simulation"
    return ac_data.get(acid)[acid]


def _vertical_separation(ac_data, acid1, acid2):
    """
    Basic vertical separation metric
    :param ac_data:
    :param acid1:
    :param acid2:
    :return:
    """

    alt1 = _get_pos(ac_data, acid1)["alt"]
    alt2 = _get_pos(ac_data, acid2)["alt"]
    vertical_sep_metres = abs(alt1 - alt2)
    vertical_sep_ft = vertical_sep_metres * _SCALE_METRES_TO_FEET

    if vertical_sep_ft < cfg.VERT_MIN_DIST:
        return cfg.LOS_SCORE

    if vertical_sep_ft < cfg.VERT_WARN_DIST:
        # Linear score between the minimum and warning distances
        return np.interp(
            vertical_sep_ft, [cfg.VERT_MIN_DIST, cfg.VERT_WARN_DIST], [cfg.LOS_SCORE, 0]
        )

    return 0


def _horizontal_separation(ac_data, acid1, acid2):

    """
    Basic horizontal separation metric
    :param ac_data:
    :param acid1:
    :param acid2:
    :return:
    """

    pos1 = _get_pos(ac_data, acid1)
    pos2 = _get_pos(ac_data, acid2)

    _, _, horizontal_sep_m = _WGS84.inv(
        pos1["lon"], pos1["lat"], pos2["lon"], pos2["lat"]
    )
    horizontal_sep_nm = round(horizontal_sep_m / _ONE_NM)

    if horizontal_sep_nm < cfg.HOR_MIN_DIST:
        return round(cfg.LOS_SCORE, 1)

    if horizontal_sep_nm < cfg.HOR_WARN_DIST:
        # Linear score between the minimum and warning distances
        return round(
            np.interp(
                horizontal_sep_nm,
                [cfg.HOR_MIN_DIST, cfg.HOR_WARN_DIST],
                [cfg.LOS_SCORE, 0],
            ),
            1,
        )

    return 0


def aircraft_separation(acid1, acid2):
    """
    Combined score based on horizontal and vertical separation.
    :param acid1:
    :param acid2:
    :return:
    """

    horizontal_sep = _horizontal_separation(acid1, acid2)
    vertical_sep = _vertical_separation(acid1, acid2)

    return max(horizontal_sep, vertical_sep)
