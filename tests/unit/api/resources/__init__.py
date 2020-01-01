"""
Package for API resource tests
"""

import datetime

import bluebird.utils.properties as props
import bluebird.utils.types as types

from tests import API_PREFIX


TEST_SIM_PROPS = props.SimProperties(
    scenario_name="TEST",
    scenario_time=0,
    seed=0,
    speed=1.0,
    state=props.SimState.INIT,
    step_size=1.0,
    utc_time=datetime.datetime.now(),
)

TEST_AIRCRAFT_PROPS = props.AircraftProperties(
    "A380",
    types.Altitude(18_500),
    "TEST1",
    types.Altitude(22_000),
    types.GroundSpeed(53),
    types.Heading(74),
    types.LatLon(51.529761, -0.127531),
    types.Altitude(25_300),
    types.VerticalSpeed(73),
)

TEST_WAYPOINT = types.Waypoint("FIX1", types.LatLon(45, 90), types.Altitude("FL225"))

TEST_ROUTE = props.AircraftRoute(
    types.Callsign("TEST"),
    [
        props.RouteItem(types.Waypoint("FIX1", types.LatLon(45, 90), None), None),
        props.RouteItem(
            types.Waypoint("FIX2", types.LatLon(50, 95), types.Altitude(321)),
            types.GroundSpeed(123),
        ),
    ],
    1,
)


def endpoint_path(endpoint):
    """Returns the endpoint path"""
    return f"{API_PREFIX}/{endpoint}"


def patch_utils_path(endpoint):
    """Returns the utils module to be patched for the given endpoint"""
    return f"bluebird.api.resources.{endpoint}.utils"
