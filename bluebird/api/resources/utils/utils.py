"""
Contains utility functions for the API resources
"""
import re
from typing import Any
from typing import Dict
from typing import Optional
from typing import Union

from flask import current_app
from flask import Response
from flask_restful import reqparse

import bluebird.api.resources.utils.responses as responses
import bluebird.utils.types as types
from bluebird.api.resources.utils.responses import bad_request_resp
from bluebird.sim_proxy.sim_proxy import SimProxy
from bluebird.utils.properties import AircraftProperties


# Name of the Flask config which contains the BlueBird instance
FLASK_CONFIG_LABEL = "bluebird_app"

# API label for aircraft callsigns. Historically this was "acid" for the BlueSky
# simulator
CALLSIGN_LABEL = "callsign"

_SCN_RE = re.compile(r"\d{2}:\d{2}:\d{2}(\.\d{1,3})?\s?>\s?.*")
_ROUTE_RE = re.compile(r"^(\*?)(\w*):((?:-|.)*)/((?:-|\d)*)$")


def parse_args(parser: reqparse.RequestParser) -> Dict[str, Any]:
    """Parse the request arguments and return them as a dict"""

    return dict(parser.parse_args(strict=True))


def try_parse_lat_lon(args: dict) -> Union[types.LatLon, Response]:
    """Attempts to parse a LatLon from an argument dict"""

    try:
        assert "lat" in args, "Expected args to contain 'lat'"
        assert "lon" in args, "Expected args to contain 'lon'"
        return types.LatLon(args["lat"], args["lon"])
    except AssertionError as exc:
        return bad_request_resp(f"Invalid LatLon: {exc}")


def sim_proxy() -> SimProxy:
    """
    Utility function to return the sim_proxy instance. This is the single point of
    entry from the API layer to the rest of the app
    """

    return current_app.config.get(FLASK_CONFIG_LABEL).sim_proxy


def check_exists(
    sim_proxy: SimProxy, callsign: types.Callsign, negate: bool = False
) -> Optional[Response]:
    """Checks if an aircraft exists, and returns an appropriate response if not"""

    exists = sim_proxy.aircraft.exists(callsign)
    if not isinstance(exists, bool):
        return responses.internal_err_resp(
            f"Could not check if the aircraft exists: {exists}"
        )
    if not exists and not negate:
        return responses.bad_request_resp(f'Aircraft "{callsign}" does not exist')
    if exists and negate:
        return responses.bad_request_resp(f'Aircraft "{callsign}" already exists')
    return None


def convert_aircraft_props(props: AircraftProperties) -> Dict[str, Any]:
    """
    Parses an AircraftProperties object into a dict suitable for returning via Flask
    """

    return {
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
