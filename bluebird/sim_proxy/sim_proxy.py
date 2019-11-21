"""
Contains the SimProxy class
"""

# TODO(RKM 2019-11-17) Invalidate caches on step() when in agent mode
# TODO(RKM 2019-11-17) Be smarter about cache use when in sandbox mode
# TODO(RKM 2019-11-17) Add functionality which never relies on any cached values. This
# may be useful in cases where we are expecting multiple clients to be interacting with
# the same simulation

import logging
from typing import Iterable, Optional

from semver import VersionInfo

from bluebird.settings import Settings
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.sim_proxy.proxy_simulator_controls import ProxySimulatorControls
from bluebird.sim_proxy.proxy_waypoint_controls import ProxyWaypointControls
from bluebird.utils.abstract_sim_client import AbstractSimClient
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls
from bluebird.utils.properties import SimMode
from bluebird.utils.timer import Timer


def _is_streaming() -> bool:
    """
    Checks if the streaming option is enabled
    """
    return Settings.STREAM_ENABLE


class SimProxy(AbstractSimClient):
    """
    Class for handling and routing requests to the simulator client
    """

    @property
    def aircraft(self) -> AbstractAircraftControls:
        return self._proxy_aircraft_controls

    @property
    def simulation(self) -> AbstractSimulatorControls:
        return self._proxy_simulator_controls

    @property
    def sim_version(self) -> VersionInfo:
        return self._sim_client.sim_version

    @property
    def waypoints(self) -> AbstractWaypointControls:
        return self._proxy_waypoint_controls

    def __init__(self, sim_client: AbstractSimClient):

        self._logger = logging.getLogger(__name__)

        # self._timer = Timer(self._log_sim_props, Settings.SIM_LOG_RATE)

        self._sim_client: AbstractSimClient = sim_client  # The actual sim_client

        # TODO(RKM 2019-11-20) In sandbox mode, we shouldn't use the proxy classes
        self._proxy_aircraft_controls = ProxyAircraftControls(self._sim_client.aircraft)
        self._proxy_waypoint_controls = ProxyWaypointControls(
            self._sim_client.waypoints
        )
        self._proxy_simulator_controls = ProxySimulatorControls(
            self._sim_client.simulation,
            self._proxy_aircraft_controls,
            self._proxy_simulator_controls,
        )

    def connect(self, timeout: int = 1) -> None:
        self._sim_client.connect(timeout)

    def start_timers(self) -> Iterable[Timer]:
        # TODO(RKM 2019-11-18) Start own timers
        return self._sim_client.start_timers()

    def stop(self, shutdown_sim: bool = False) -> bool:
        raise NotImplementedError

    def start_timer(self):
        """
        Starts the timer for logging
        :return:
        """
        # TODO(RKM 2019-11-18) Start any child timers
        self._timer.start()
        self._logger.info(
            f"Logging started. Initial SIM_LOG_RATE={Settings.SIM_LOG_RATE}"
        )
        return self._timer

    def shutdown(self, shutdown_sim: bool = False) -> bool:
        """
        Shutdown the sim client
        :param shutdown_sim: If true, and if the simulation server supports it, will
        also send a shutdown command
        :return: If shutdown_sim was requested, the return value will indicate whether
        the simulator was shut down successfully. Always returns True if shutdown_sim
        was not requested
        """
        return self._sim_client.shutdown(shutdown_sim)

    def set_mode(self, mode: SimMode) -> Optional[str]:
        raise NotImplementedError
        # if is_agent_mode():
        #     err = sim_proxy().simulation.pause()
        #     if err:
        #         return responses.internal_err_resp(
        #             f"Could not pause sim when changing mode: {err}"
        #         )

        # elif Settings.SIM_MODE == _SimMode.Sandbox:
        #     err = sim_proxy().start_or_resume_sim()
        #     if err:
        #         return responses.internal_err_resp(
        #             f"Could not resume sim when changing mode: {err}"
        #         )
        # else:
        #     # Only reach here if we add a new mode to settings but don't add a case to
        #     # handle it here
        #     raise ValueError(f"Unsupported mode {Settings.SIM_MODE}")

        # return responses.ok_resp()

    def _log_ac_data(self):
        pass

    # def contains(self, callsign: types.Callsign) -> bool:
    #     """
    #     Checks if the given callsign exists in the simulation
    #     :param callsign:
    #     """
    #     return (
    #         self._ac_data.contains(callsign)
    #         if _is_streaming()
    #         else bool(self._sim_client.aircraft.get_properties(callsign))
    #     )

    # def get_aircraft_props(
    #     self, callsign: types.Callsign
    # ) -> Tuple[Optional[AircraftProperties], int]:
    #     """
    #     Get properties for the specified aircraft
    #     :param callsigns:
    #     :return:
    #     """

    #     props = (
    #         self._ac_data.store.get(callsign, None)
    #         if _is_streaming()
    #         else self._sim_client.aircraft.get_properties(callsign)
    #     )

    #     sim_t = int(self._sim_client.simulation.time)
    #     return (props, sim_t)

    # def get_all_aircraft_props(self) -> Tuple[List[AircraftProperties], int]:

    #     props, sim_t = (
    #         self._ac_data.get_all_properties()
    #         if _is_streaming()
    #         else self._sim_client.aircraft.get_all_properties()
    #     )

    #     # sim_t = int(self._sim_client.simulation.get_time())
    #     return props, sim_t

    # def set_cleared_fl(
    #     self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    # ) -> Optional[str]:
    #     """


#     Set the cleared flight level for the specified aircraft
#     :param callsign: The aircraft identifier
#     :param flight_level: The flight level to set
#     :returns None: If cleared flight level was set
#     :returns str: To indicate an error
#     :return:
#     """

#     resp = self._sim_client.aircraft.set_cleared_fl(
#         callsign, flight_level, **kwargs
#     )

#     if resp:
#         return resp

#     # TODO
#     # self._ac_data.set_cleared_fl(callsign, flight_level)
#     return None

# def pause_sim(self) -> Optional[str]:
#     # TODO What else do we need to handle here? (see BlueSky's client class)
#     # ac_data().set_log_rate(0)
#     err = self._sim_client.simulation.pause()
#     return err

# def resume_sim(self) -> Optional[str]:
#     # TODO What else do we need to handle here? (see BlueSky's client class,
#     # and old ac_data)
#     # ac_data().resume_log()
#     # TODO Start or resume
#     err = self._sim_client.simulation.resume()
#     return err

# def reset_sim(self) -> Optional[str]:
#     # TODO What else do we need to handle here? (see BlueSky's client class)
#     # - Clear all data
#     # - Stop episode logging
#     # - reset sim state to "init"
#     err = self._sim_client.simulation.reset()
#     return err

# def stop_sim(self, shutdown_sim: bool = False) -> bool:
#     # TODO What else to do here?
#     shutdown_ok = self._sim_client.stop(shutdown_sim)
#     return shutdown_ok

# def load_scenario(
#     self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
# ) -> Optional[str]:
#     # TODO What else do we need to handle here? (see BlueSky's client class)
#     # TODO Check aircraft data repopulated (if streaming)
#     # TODO Handle this in BlueSky sim_client
#     # if not filename.lower().endswith(".scn"):
#     #     filename += ".scn"
#     # TODO If start_paused specified, don't return until this is confirmed
#     # if not wait_until_eq(sim_state(), 1):
#     #     return internal_err_resp(
#     #         "Could not pause simulation after starting new scenario"
#     #     )

#     err = self._sim_client.simulation.load_scenario(
#         scenario_name, speed, start_paused
#     )
#     return err

# @property
# def sim_properties(self) -> SimProperties:
#     props = (
#         self._sim_props
#         if _is_streaming()
#         else self._sim_client.simulation.properties
#     )

#     # TODO Probably a better way of doing this
#     if not isinstance(props, SimProperties):
#         err_str = "Couldn't get a value for SimProperties"
#         if isinstance(props, str):
#             err_str += f"({props})"
#         raise AttributeError(err_str)

#     return props

# def set_sim_speed(self, speed: float) -> Optional[str]:
#     err = self._sim_client.simulation.set_speed(speed)
#     if err:
#         return err

#     # TODO Update log rate
#     # ac_data().set_log_rate(multiplier)
#     return None

# @property
# def seed(self):
#     return self._seed

# def set_seed(self, seed: int) -> Optional[str]:
#     err = self._sim_client.simulation.set_seed(seed)
#     if err:
#         return err
#     self._seed = seed
#     return None

# def upload_new_scenario(
#     self, scn_name: str, content: Iterable[str]
# ) -> Optional[str]:
#     # TODO What else do we need to do here?
#     store_local_scn(scn_name, content)
#     err = self._sim_client.simulation.upload_new_scenario(scn_name, content)
#     return err

# def step_sim(self) -> Optional[str]:
#     # TODO Clients need to assert that the simulation is stepped. If streaming, we
#     # also need to wait for ac_data to be updated
#     err = self._sim_client.simulation.step()
#     if err:
#         return err

#     # TODO
#     # self._ac_data.log()
#     return None

# TODO(RKM 2019-11-17) Move to new ProxyWaypointControl class
# def define_waypoint(
#     self, name: str, position: types.LatLon, **kwargs
# ) -> Optional[str]:
#     err = self._sim_client.waypoints.define(name, position, **kwargs)
#     if err:
#         return err
#     # TODO We may want to do something here after passing the request to the sim
#     return None

# def add_waypoint_to_route(
#     self, callsign: types.Callsign, target: Union[str, types.LatLon], **kwargs
# ) -> Optional[str]:
#     err = self._sim_client.aircraft.add_waypoint_to_route(
#         callsign, target, **kwargs
#     )
#     if err:
#         return err
#     # TODO We may want to do something here after passing the request to the sim
#     return None
