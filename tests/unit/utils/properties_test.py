"""
Tests for the properties module
"""
import bluebird.utils.types as types
from bluebird.utils.properties import AircraftProperties
from tests.data import TEST_SCENARIO


def test_aircraft_properties_from_data():
    aircraft_data = TEST_SCENARIO["aircraft"][0]
    assert AircraftProperties.from_data(aircraft_data) == AircraftProperties(
        aircraft_type=aircraft_data["type"],
        altitude=types.Altitude(f'FL{aircraft_data["currentFlightLevel"]}'),
        callsign=types.Callsign(aircraft_data["callsign"]),
        cleared_flight_level=types.Altitude(f'FL{aircraft_data["clearedFlightLevel"]}'),
        ground_speed=None,
        heading=None,
        initial_flight_level=types.Altitude(f'FL{aircraft_data["currentFlightLevel"]}'),
        position=types.LatLon(
            aircraft_data["startPosition"][1], aircraft_data["startPosition"][0]
        ),
        requested_flight_level=types.Altitude(
            f'FL{aircraft_data["requestedFlightLevel"]}'
        ),
        route_name=None,
        vertical_speed=None,
    )
