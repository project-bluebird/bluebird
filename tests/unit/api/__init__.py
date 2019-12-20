"""
Package for API tests
"""

# TODO(RKM 2019-11-24) The tests in this package need refactored to use mock

import bluebird.utils.types as types


TEST_LAT = 55.945290
TEST_LON = -3.187293

TEST_LATLON = types.LatLon(TEST_LAT, TEST_LON)


class MockSimProxy:
    """Mock SimProxy for the API tests"""

    @property
    def aircraft(self):
        return self._mock_aircraft_controls

    @property
    def simulation(self):
        return self._mock_simulator_controls

    @property
    def waypoints(self):
        return self._mock_waypoint_controls

    @property
    def sector(self):
        return self._sector

    @sector.setter
    def sector(self, sector):
        self._sector = sector

    def __init__(self):
        self._mock_aircraft_controls = None
        self._mock_simulator_controls = None
        self._mock_waypoint_controls = None

    def set_props(self, aircraft_controls, simulator_controls, waypoint_controls):
        self._mock_aircraft_controls = aircraft_controls
        self._mock_simulator_controls = simulator_controls
        self._mock_waypoint_controls = waypoint_controls


class MockBlueBird:
    """Mock BlueBird class for the API tests"""

    def __init__(self):
        self.sim_proxy = MockSimProxy()
        self.metrics_providers = []
