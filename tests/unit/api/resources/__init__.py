"""
Package for API resource tests
"""
import datetime

import mock

import bluebird.utils.properties as props
import bluebird.utils.types as types
from bluebird.api.resources.utils.utils import FLASK_CONFIG_LABEL
from tests import API_PREFIX


TEST_SIM_PROPS = props.SimProperties(
    sector_name="test-sector",
    scenario_name="test-scenario",
    scenario_time=0,
    seed=0,
    speed=1.0,
    state=props.SimState.INIT,
    dt=0.01,
    utc_datetime=datetime.datetime.now(),
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
    None,
)


def endpoint_path(endpoint: str) -> str:
    """Returns the endpoint path"""
    return f"{API_PREFIX}/{endpoint}"


# TODO(rkm 2020-01-12) Aiming to remove this since the tests can be simplified by using
# get_app_mock
def patch_utils_path(endpoint: str) -> str:
    """Returns the utils module to be patched for the given endpoint"""
    return f"bluebird.api.resources.{endpoint}.utils"


def get_app_mock(test_flask_client):
    app_mock = mock.Mock()
    test_flask_client.application.config[FLASK_CONFIG_LABEL] = app_mock
    return app_mock
