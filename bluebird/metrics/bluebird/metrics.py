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

from aviary.metrics.separation_metric import pairwise_separation_metric

from bluebird.api.resources.utils.utils import sim_proxy
from bluebird.metrics.bluebird import config as cfg
from bluebird.utils.strings import is_acid
from bluebird.utils.types import Callsign
import bluebird.api.resources.utils.utils as utils


def aircraft_separation(acid1, acid2):
    """
    Combined score based on horizontal and vertical separation.
    :param acid1:
    :param acid2:
    :return:
    """

    props1 = sim_proxy().aircraft.properties(Callsign(acid1))
    props2 = sim_proxy().aircraft.properties(Callsign(acid2))

    return pairwise_separation_metric(
        lon1=props1.position.lon_degrees,
        lat1=props1.position.lat_degrees,
        alt1=props1.altitude.meters,
        lon2=props2.position.lon_degrees,
        lat2=props2.position.lat_degrees,
        alt2=props2.altitude.meters
    )
