"""
BlueBird's built-in metrics, provided by Aviary
"""

# TODO(RKM 2019-12-12) Maybe suggest using __all__ in Aviary to only expose the required
# API functions
import aviary.metrics as aviary_metrics

import bluebird.utils.types as types
import bluebird.utils.properties as props
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls


# TODO Update metrics docs
def pairwise_separation_metric(*args, **kwargs):
    """
    The Aviary aircraft separation metric function. Expected *args are two aircraft
    callsigns.
    See: https://github.com/alan-turing-institute/aviary/blob/develop/aviary/metrics/separation_metric.py # noqa: E501
    """

    assert len(args) == 2 and all(
        isinstance(x, str) for x in args
    ), "Expected 2 string arguments"

    aircraft_controls: AbstractAircraftControls = kwargs["aircraft_controls"]

    props1 = aircraft_controls.properties(types.Callsign(args[0]))
    if not isinstance(props1, props.AircraftProperties):
        err_resp = f": {props1}" if props1 else ""
        raise ValueError(f"Could not get properties for {args[0]}{err_resp}")

    props2 = aircraft_controls.properties(types.Callsign(args[1]))
    if not isinstance(props2, props.AircraftProperties):
        err_resp = f": {props2}" if props2 else ""
        raise ValueError(f"Could not get properties for {args[1]}{err_resp}")

    return aviary_metrics.pairwise_separation_metric(
        lon1=props1.position.lon_degrees,
        lat1=props1.position.lat_degrees,
        alt1=props1.altitude.meters,
        lon2=props2.position.lon_degrees,
        lat2=props2.position.lat_degrees,
        alt2=props2.altitude.meters,
    )


def sector_exit_metric(*args, **kwargs):
    """
    The Aviary sector exit metric function. Expected *args are:
    []
    See: https://github.com/alan-turing-institute/aviary/blob/develop/aviary/metrics/sector_exit_metric.py # noqa: E501
    """

    # TODO(RKM 2019-12-12) Args are;
    # current_lon,
    # current_lat,
    # current_alt,
    # previous_lon,
    # previous_lat,
    # previous_alt,
    # requested_flight_level,
    # sector,
    # route,
    # hor_warn_dist=HOR_WARN_DIST,
    # hor_max_dist=HOR_MAX_DIST,
    # vert_warn_dist=VERT_WARN_DIST,
    # vert_max_dist=VERT_MAX_DIST
    # return aviary_metrics.sector_exit_metric()

    return aviary_metrics.sector_exit_metric()
