"""
Contains the SimProxy class
"""

import logging
from typing import Optional, Tuple, List, Iterable, Union

from bluebird.logging import store_local_scn
from bluebird.sim_client.abstract_sim_client import AbstractSimClient
from bluebird.sim_proxy.aircraft_data_cache import AircraftDataCache
from bluebird.settings import Settings
from bluebird.utils.types import Altitude, Callsign, LatLon
from bluebird.utils.properties import AircraftProperties, SimProperties, SimState
from bluebird.utils.timer import Timer


def _is_streaming():
    """
    Checks if the streaming option is enabled
    """
    return Settings.STREAM_ENABLE


class SimProxy:
    """
    Class for handling and routing requests to the simulator client.

    Note that the API layer is free to use the sim client directly, however this class
    can be used as a passthrough in order to redcue calls to the simulator (if in
    streaming mode and using the AircraftDataCache) or for handling any commands which
    require special processing before the request is passed to the simulator
    """

    def __init__(self, sim_client: AbstractSimClient):

        self._logger = logging.getLogger(__name__)

        self._timer = Timer(self._log_sim_props, Settings.SIM_LOG_RATE)

        # TODO Need to hook this up to read from sim_client if streaming, and wait for
        # it to be initially set on startup
        self._sim_props = None

        self._sim_client: AbstractSimClient = sim_client
        self._ac_data = AircraftDataCache()

        # TODO What do we need this for?
        self._seed = None

    def start_timer(self):
        """
        Starts the timer for logging
        :return:
        """

        self._timer.start()
        self._logger.info(
            f"Logging started. Initial SIM_LOG_RATE={Settings.SIM_LOG_RATE}"
        )
        return self._timer

    def contains(self, callsign: Callsign) -> bool:
        """
        Checks if the given callsign exists in the simulation
        :param callsign:
        """
        return (
            self._ac_data.contains(callsign)
            if _is_streaming()
            else bool(self._sim_client.aircraft.get_properties(callsign))
        )

    def get_aircraft_props(
        self, callsign: Callsign
    ) -> Tuple[Optional[AircraftProperties], int]:
        """
        Get properties for the specified aircraft
        :param callsigns:
        :return:
        """

        props = (
            self._ac_data.store.get(callsign, None)
            if _is_streaming()
            else self._sim_client.aircraft.get_properties(callsign)
        )

        sim_t = int(self._sim_client.simulation.get_time())
        return (props, sim_t)

    def get_all_aircraft_props(self) -> Tuple[List[AircraftProperties], int]:

        props = (
            self._ac_data.get_all_properties()
            if _is_streaming()
            else self._sim_client.aircraft.get_all_properties()
        )

        sim_t = int(self._sim_client.simulation.get_time())
        return (props, sim_t)

    def set_cleared_fl(
        self, callsign: Callsign, flight_level: Altitude, **kwargs
    ) -> Optional[str]:
        """
		Set the cleared flight level for the specified aircraft
		:param callsign: The aircraft identifier
		:param flight_level: The flight level to set
		:returns None: If cleared flight level was set
		:returns str: To indicate an error
		:return:
		"""

        resp = self._sim_client.aircraft.set_cleared_fl(
            callsign, flight_level, **kwargs
        )

        if resp:
            return resp

        # TODO
        # self._ac_data.set_cleared_fl(callsign, flight_level)
        return None

    def start_or_resume_sim(self) -> Optional[str]:
        # TODO What else do we need to handle here? (see BlueSky's client class,
        # and old ac_data)
        # ac_data().resume_log()

        props = self._sim_client.simulation.properties
        if isinstance(props, str):
            return props

        err = None
        if props.state == SimState.INIT:
            err = self._sim_client.simulation.resume()
        elif props.state == SimState.HOLD:
            err = self._sim_client.simulation.start()
        elif props.state == SimState.END:
            err = "Invalid initial state. Sim is stopped"

        return err

    def pause_sim(self) -> Optional[str]:
        # TODO What else do we need to handle here? (see BlueSky's client class)
        # ac_data().set_log_rate(0)

        props = self._sim_client.simulation.properties
        if isinstance(props, str):
            return props

        if props.state == SimState.RUN:
            err = self._sim_client.simulation.pause()
        elif props.state == SimState.HOLD:
            err = None
        else:
            err = f"Invalid initial state: {props.state.name}"

        return err

    def reset_sim(self) -> Optional[str]:
        # TODO What else do we need to handle here? (see BlueSky's client class)
        # - Clear all data
        # - Stop episode logging

        props = self._sim_client.simulation.properties
        if isinstance(props, str):
            return props

        return (
            self._sim_client.simulation.reset()
            if props.state == SimState.RUN or props.state == SimState.HOLD
            else f"Invalid initial state: {props.state.name}"
        )

    def stop_client(self, shutdown_sim: bool = False) -> bool:
        # TODO What else to do here? - Maybe close logging?
        return self._sim_client.stop(shutdown_sim)

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        # TODO What else do we need to handle here? (see BlueSky's client class)
        # TODO Check aircraft data repopulated (if streaming)
        # TODO Handle this in BlueSky sim_client
        # if not filename.lower().endswith(".scn"):
        #     filename += ".scn"
        # TODO If start_paused specified, don't return until this is confirmed
        # if not wait_until_eq(sim_state(), 1):
        #     return internal_err_resp(
        #         "Could not pause simulation after starting new scenario"
        #     )

        err = self._sim_client.simulation.load_scenario(
            scenario_name, speed, start_paused
        )
        return err

    @property
    def sim_properties(self) -> SimProperties:
        """
        :return: The current sim properties, either from the proxy value or from a sim
        request
        """

        props = (
            self._sim_props
            if _is_streaming()
            else self._sim_client.simulation.properties
        )

        if not isinstance(props, SimProperties):
            raise RuntimeError(f"Could not get the sim properties: {props}")

        return props

    def set_sim_speed(self, speed: float) -> Optional[str]:

        err = self._sim_client.simulation.set_speed(speed)

        if err:
            return err

        # TODO Update log rate
        # ac_data().set_log_rate(multiplier)
        return None

    @property
    def seed(self):
        return self._seed

    def set_seed(self, seed: int) -> Optional[str]:
        err = self._sim_client.simulation.set_seed(seed)
        if err:
            return err
        self._seed = seed
        return None

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        # TODO What else do we need to do here?
        store_local_scn(scn_name, content)
        err = self._sim_client.simulation.upload_new_scenario(scn_name, content)
        return err

    def step_sim(self) -> Optional[str]:
        # TODO Clients need to assert that the simulation is stepped. If streaming, we
        # also need to wait for ac_data to be updated
        err = self._sim_client.simulation.step()
        if err:
            return err

        # TODO
        # self._ac_data.log()
        return None

    def define_waypoint(self, name: str, position: LatLon, **kwargs) -> Optional[str]:
        err = self._sim_client.waypoints.define(name, position, **kwargs)
        if err:
            return err
        # TODO We may want to do something here after passing the request to the sim
        return None

    def add_waypoint_to_route(
        self, callsign: Callsign, target: Union[str, LatLon], **kwargs
    ) -> Optional[str]:
        err = self._sim_client.aircraft.add_waypoint_to_route(
            callsign, target, **kwargs
        )
        if err:
            return err
        # TODO We may want to do something here after passing the request to the sim
        return None

    def _log_sim_props(self):

        props = self.sim_properties

        if isinstance(props, str):
            self._logger.error(f"Could not get sim properties: {props}")
            return

        data = (
            f"speed={props.sim_speed}x, ticks={props.sim_t:4}, time={props.sim_utc}, "
            f"state={props.sim_state.name}, aircraft={props.ac_count}"
        )
        self._logger.info(data)

    def _log_ac_data(self):
        pass

