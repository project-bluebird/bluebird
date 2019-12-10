"""
Contains utility functions for the API resources
"""

import re
from typing import Optional, Dict, Any, Union

from flask import current_app, Response
from flask_restful import reqparse

import bluebird.utils.types as types
import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.responses import bad_request_resp
from bluebird.metrics import MetricsProviders
from bluebird.sim_proxy.sim_proxy import SimProxy
from bluebird.utils.properties import AircraftProperties, AircraftRoute


# Name of the Flask config which contains the BlueBird instance
FLASK_CONFIG_LABEL = "bluebird_app"

# API label for aircraft callsigns. Historically this was "acid" for the BlueSky
# simulator
CALLSIGN_LABEL = "acid"

_SCN_RE = re.compile(r"\d{2}:\d{2}:\d{2}(\.\d{1,3})?\s?>\s?.*")
_ROUTE_RE = re.compile(r"^(\*?)(\w*):((?:-|.)*)/((?:-|\d)*)$")


def parse_args(parser: reqparse.RequestParser) -> Dict[str, Any]:
    """Parse the request arguments and return them as a dict"""
    return dict(parser.parse_args(strict=True))


def try_parse_lat_lon(args: dict) -> Union[types.LatLon, Response]:
    """
    Attempts to parse a LatLon from an argument dict
    :param args:
    :return:
    """
    try:
        assert "lat" in args, "Expected args to contain 'lat'"
        assert "lon" in args, "Expected args to contain 'lon'"
        return types.LatLon(args["lat"], args["lon"])
    except AssertionError as exc:
        return bad_request_resp(f"Invalid LatLon: {exc}")


def _bb_app():
    """Gets the BlueBird app instance"""
    if not hasattr(_bb_app, "_instance"):
        _bb_app._instance = current_app.config.get(FLASK_CONFIG_LABEL)
    return _bb_app._instance


def sim_proxy() -> SimProxy:
    """
    Utility function to return the sim_proxy instance. This is the single point of
    entry from the API layer to the rest of the app
    """
    return _bb_app().sim_proxy


def metrics_providers() -> MetricsProviders:
    """Utility function to return the metrics_providers instance"""
    return _bb_app().metrics_providers


def check_exists(callsign: types.Callsign, negate: bool = False) -> Optional[Response]:
    """Checks if an aircraft exists, and returns an appropriate response if not"""
    exists = sim_proxy().aircraft.exists(callsign)
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

    # TODO(RKM 2019-11-23) BlueSky doesn't give us this info, so have to add it
    # ourselves in bluesky_aircraft controls
    cfl = props.cleared_flight_level.feet if props.cleared_flight_level else None
    rfl = props.requested_flight_level.feet if props.requested_flight_level else None

    data = {
        str(props.callsign): {
            "actype": props.aircraft_type,
            "cleared_fl": cfl,
            "current_fl": props.altitude.feet,
            "gs": props.ground_speed.meters_per_sec,
            "hdg": props.heading.degrees,
            "lat": props.position.lat_degrees,
            "lon": props.position.lon_degrees,
            "requested_fl": rfl,
            "vs": props.vertical_speed.feet_per_min,
        }
    }

    return data


# NOTE(RKM 2019-11-19) Only the waypoint names are currently returned. Do we want to
# (optionally) also return their full lat/lon?
def convert_aircraft_route(route: AircraftRoute) -> Dict[str, Any]:
    """
    Parses an AircraftRoute object into a dict suitable for returning via Flask
    """

    callsign_str = str(route.callsign)

    data = {
        callsign_str: {
            "route": [],
            "current_segment_index": route.current_segment_index,
        }
    }

    for segment in route.segments:
        data[callsign_str]["route"].append(
            {
                "wpt_name": segment.waypoint.name,
                "req_alt": (
                    segment.waypoint.altitude.feet
                    if segment.waypoint.altitude
                    else None
                ),
                "req_gspd": (
                    segment.required_gspd.feet_per_sec
                    if segment.required_gspd
                    else None
                ),
            }
        )

    return data
