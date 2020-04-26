"""
Tests for the properties module
"""
from bluebird.utils.properties import AircraftProperties
from bluebird.utils.types import LatLon
from tests.data import TEST_SCENARIO


def test_aircraft_properties_from_data():
    aircraft_data = TEST_SCENARIO["aircraft"][0]
    AircraftProperties.from_data(aircraft_data) == AircraftProperties(
        aircraft_type=aircraft_data["type"],
        altitude=aircraft_data["currentFlightLevel"],
        callsign=aircraft_data["callsign"],
        cleared_flight_level=aircraft_data["clearedFlightLevel"],
        ground_speed=None,
        heading=None,
        initial_flight_level=aircraft_data["currentFlightLevel"],
        position=LatLon(
            aircraft_data["startPosition"][0], aircraft_data["startPosition"][1]
        ),
        requested_flight_level=aircraft_data["requestedFlightLevel"],
        route_name=None,
        vertical_speed=None,
    )
