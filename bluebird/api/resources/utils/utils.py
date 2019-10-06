"""
Contains utility functions for the API resources
"""

import logging
import re
import time
from typing import List, Union, Optional, Dict, Any

from flask import current_app
from flask_restful import reqparse

from bluebird.api.resources.utils.responses import RespTuple, bad_request_resp
from bluebird.metrics.abstract_metrics_provider import AbstractMetricProvider
from bluebird.settings import Settings
from bluebird.utils.properties import SimMode
from bluebird.utils.types import LatLon, Callsign


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


def try_parse_lat_lon(args: dict) -> Union[LatLon, RespTuple]:
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


# def sim_client() -> AbstractSimClient:
#     """
#     Utility function to return the sim_client instance
#     """
#     return _bb_app().sim_client


# def ac_data() -> AcDataCache:
#     """
#     Utility function to return the ac_data instance
#     """
#     return _bb_app().ac_data


# def sim_state() -> SimState:
#     """
#     Utility function to return the sim_state instance
#     """
#     return _bb_app().sim_state


# NOTE This is probably ok here
def metrics_providers() -> List[AbstractMetricProvider]:
    """
    Utility function to return the metrics_providers instance
    """
    return _bb_app().metrics_providers


# TODO Old version of this checked multiple strings at once - need to modify or change
# usage
# TODO Only directly check ac_data if settings.streaming
def check_callsign_exists(callsign: Callsign) -> Optional[RespTuple]:
    """
    Asserts that the given callsign exists in the scenario
    :param callsign:
    :return:
    """

    if not ac_data().store:
        return bad_request_resp("No aircraft in the simulaton")

    if not ac_data().contains(str(callsign)):
        return bad_request_resp(f"Aircraft {callsign} was not found")

    return None


def wait_until_eq(lhs, rhs, max_wait=1) -> bool:
    """
    Waits for the given condition to be met
    :param lhs:
    :param rhs:
    :param max_wait:
    :return:
    """

    timeout = time.time() + max_wait

    while bool(lhs) != bool(rhs):
        time.sleep(0.1)
        if time.time() > timeout:
            return False

    return True


# TODO Move to  sim proxy layer
def check_ac_data_populated() -> Optional[str]:
    """
    Checks if the ac_data is populated after resetting or loading a new scenario
    :return:
    """

    if not wait_until_eq(ac_data().store, True):
        return (
            "No aircraft data received after loading. This may have been caused by the "
            "given scenario not containing any aircraft"
        )

    return None


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


def is_agent_mode() -> bool:
    """
    Checks if we are currently in Agent mode
    """
    return Settings.SIM_MODE == SimMode.Agent
