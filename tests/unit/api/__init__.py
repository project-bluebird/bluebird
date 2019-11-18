"""
Package for API tests
"""

from bluebird.utils.properties import SimProperties
import bluebird.utils.types as types


TEST_LAT = 55.945290
TEST_LON = -3.187293

TEST_LATLON = types.LatLon(TEST_LAT, TEST_LON)


# class MockAircraftControls_:
#     """
#     Simple test mock of AbstractAircraftControls
#     """

#     def __init__(self):
#         self.created_aricraft = None
#         self._set_hdg_called = False

#     def create(self, *args):
#         self.created_aricraft = list(args)

#     def direct_to_waypoint(self, callsign: types.Callsign, waypoint: str):
#         assert isinstance(callsign, types.Callsign)
#         if not waypoint.upper() == "FIX":
#             return "Invalid waypoint"
#         return None

#     def set_heading(self, callsign: types.Callsign, heading: types.Heading):
#         if not self._set_hdg_called:
#             self._set_hdg_called = True
#             raise NotImplementedError
#         assert isinstance(heading, types.Heading)
#         if not str(callsign) == "TEST":
#             return "Invalid callsign"
#         return None


# class MockSimClient_:
#     """
#     Simple test mock of a SimClient
#     """

#     @property
#     def aircraft(self):
#         return self._aircraft_controls

#     def __init__(self, aircraft_controls):
#         self._aircraft_controls = aircraft_controls


# class MockSimProxy:
#     """
#     Simple test mock of the SimProxy class
#     """

#     @property
#     def sim_properties(self) -> SimProperties:
#         if not self._props_called:
#             self._props_called = True
#             raise AttributeError
#         return SimProperties(SimState.RUN, 1.0, 1.0, 0.0, "test_scn")

#     def __init__(self):
#         self.last_cfl = self.last_wpt = self.last_direct = self.last_scn = None
#         self._props_called = self._reset_flag = self._pause_called = False
#         self._get_route_called = self._resume_called = False

#     def set_cleared_fl(
#         self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
#     ):
#         self.last_cfl = {"callsign": callsign, "flight_level": flight_level, **kwargs}

#     def get_aircraft_props(self, callsign: types.Callsign):
#         if not self.contains(callsign):
#             return (None, 31)
#         return (
#             AircraftProperties(
#                 "A380",
#                 types.Altitude(18_500),
#                 callsign,
#                 types.Altitude(22_000),
#                 types.GroundSpeed(53),
#                 types.Heading(74),
#                 types.LatLon(51.529761, -0.127531),
#                 types.Altitude(25_300),
#                 types.VerticalSpeed(73),
#             ),
#             42,
#         )

#     def contains(self, callsign: types.Callsign):
#         # "TEST*" aircraft exist, all others do not
#         return str(callsign).upper().startswith("TEST")

#     def define_waypoint(self, name: str, position: types.LatLon, **kwargs):
#         self.last_wpt = None
#         if kwargs["type"] and kwargs["type"] != "FIX":
#             return "Invalid waypoint type"
#         self.last_wpt = {"name": name, "position": position, **kwargs}

#     def direct_to_waypoint(self, callsign: types.Callsign, waypoint: str):
#         self.last_direct = {"callsign": callsign, "waypoint": waypoint}

#     def set_sim_speed(self, speed: float):
#         return None if speed < 50 else "Requested speed too large"

#     def reset_sim(self):
#         if self._reset_flag:
#             return None
#         self._reset_flag = True
#         return "Error!"

#     def pause_sim(self):
#         if not self._pause_called:
#             self._pause_called = True
#             return "Couldn't pause sim"
#         return None

#     def load_scenario(
#         self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
#     ):
#         self.last_scn = {
#             "scenario_name": scenario_name,
#             "speed": speed,
#             "start_paused": start_paused,
#         }

#     def get_aircraft_route(self, callsign: types.Callsign):
#         assert callsign
#         if not self._get_route_called:
#             self._get_route_called = True
#             return "Could not get aircraft route"
#         return ["A", "B"]  # TODO What should the route look like?

#     def resume_sim(self):
#         if not self._resume_called:
#             self._resume_called = True
#             return "Couldn't resume sim"
#         return None


class MockSimProxy:
    """Mock SimProxy for the API tests"""

    # pylint:disable=missing-docstring

    @property
    def aircraft(self):
        return self._mock_aircraft_controls

    @property
    def simulation(self):
        return self._mock_simulator_controls

    @property
    def waypoints(self):
        return self._mock_waypoint_controls

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

    # pylint:disable=too-few-public-methods

    def __init__(self):
        self.sim_proxy = MockSimProxy()
        self.metrics_providers = []
