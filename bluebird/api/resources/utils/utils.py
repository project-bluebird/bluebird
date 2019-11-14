"""
Contains utility functions for the API resources
"""

import logging
import re
from typing import List, Optional, Dict, Any

from flask import current_app
from flask_restful import reqparse

from bluebird.api.resources.utils.responses import bad_request_resp
from bluebird.metrics.abstract_metrics_provider import AbstractMetricProvider
from bluebird.sim_client.abstract_sim_client import AbstractSimClient
from bluebird.sim_proxy.sim_proxy import SimProxy
from bluebird.utils.properties import AircraftProperties
from bluebird.utils.types import LatLon


_LOGGER = logging.getLogger(__name__)

# Name of the Flask config which contains the BlueBird instance
FLASK_CONFIG_LABEL = "bluebird_app"

# API label for aircraft callsigns. Historically this was "acid" for the BlueSky
# simulator
CALLSIGN_LABEL = "acid"

_SCN_RE = re.compile(r"\d{2}:\d{2}:\d{2}(\.\d{1,3})?\s?>\s?.*")
_ROUTE_RE = re.compile(r"^(\*?)(\w*):((?:-|.)*)/((?:-|\d)*)$")


def parse_args(parser: reqparse.RequestParser) -> Dict[str, Any]:
    """
    Parse the request arguments and return them as a dict
    """
    return dict(parser.parse_args(strict=True))


def try_parse_lat_lon(args: dict):  # -> Union[LatLon, RespTuple]:
    """
    Attempts to parse a LatLon from an argument dict
    :param args:
    :return:
    """
    try:
        assert "lat" in args, "Expected args to contain 'lat'"
        assert "lon" in args, "Expected args to contain 'lon'"
        return LatLon(args["lat"], args["lon"])
    except AssertionError as exc:
        return bad_request_resp(f"Invalid LatLon: {exc}")


def _bb_app():
    """
    Gets the BlueBird app instance
    """
    # pylint: disable=protected-access
    if not hasattr(_bb_app, "_instance"):
        _bb_app._instance = current_app.config.get(FLASK_CONFIG_LABEL)
    return _bb_app._instance


def sim_proxy() -> SimProxy:
    """
    Utility function to return the sim_proxy instance
    """
    return _bb_app().sim_proxy


def sim_client() -> AbstractSimClient:
    """
    Utility function to return the sim_client instance
    """
    return _bb_app().sim_client


def metrics_providers() -> List[AbstractMetricProvider]:
    """
    Utility function to return the metrics_providers instance
    """
    return _bb_app().metrics_providers


# TODO This is specific to BlueSky and will be replaced
def validate_scenario(scn_lines: List[str]) -> Optional[str]:
    """
    Checks that each line in the given list matches the requirements
    :param scn_lines:
    :return:
    """

    for line in scn_lines:
        if not _SCN_RE.match(line):
            return f"Line '{line}' does not match the required format"

    return None


# TODO Move to the BlueSky client utils
def parse_route_data(route_data):
    """
    Parse a list of strings containing route data into a keyed dictionary
    :param route_data:
    :return:
    """

    parsed = []
    for line in map(lambda s: s.replace(" ", ""), route_data):
        match = _ROUTE_RE.match(line)
        if not match:
            return line
        req_alt = match.group(3) if not "-" in match.group(3) else None
        req_spd = int(match.group(4)) if not "-" in match.group(4) else None
        parsed.append(
            {
                "is_current": bool(match.group(1)),
                "wpt_name": match.group(2),
                "req_alt": req_alt,
                "req_spd": req_spd,
            }
        )
    return parsed


def convert(props: AircraftProperties) -> Dict[str, Any]:
    """
    Parses an AircraftProperties object into a dict suitable for returning via Flask
    :param props:
    :return:
    """

    # TODO Check units
    # vs - feet per min OR feet per sec?
    data = {
        str(props.callsign): {
            "actype": props.aircraft_type,
            "cleared_fl": props.cleared_flight_level.feet,
            "current_fl": props.altitude.feet,
            "gs": props.ground_speed.meters_per_sec,
            "hdg": props.heading.degrees,
            "lat": props.position.lat_degrees,
            "lon": props.position.lon_degrees,
            "requested_fl": props.requested_flight_level.feet,
            "vs": props.vertical_speed.feet_per_min,
        }
    }
    return data
