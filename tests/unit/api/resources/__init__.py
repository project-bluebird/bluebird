"""
Package for API resource tests
"""

import bluebird.utils.types as types
from bluebird.utils.properties import AircraftProperties


TEST_AIRCRAFT_PROPS = AircraftProperties(
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


def patch_path(endpoint):
    """Returns the module to be patched for the API tests"""
    return f"bluebird.api.resources.{endpoint}.utils"
