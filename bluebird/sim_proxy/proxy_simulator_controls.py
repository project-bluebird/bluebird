"""
Contains the ProxySimulatorControls class
"""

import logging

from typing import Optional, Union, Iterable

from bluebird.settings import Settings
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.sim_proxy.proxy_waypoint_controls import ProxyWaypointControls
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls
from bluebird.utils.properties import SimProperties
from bluebird.utils.timer import Timer
from bluebird.utils.timeutils import timeit
from bluebird.utils.types import is_valid_seed


class ProxySimulatorControls(AbstractSimulatorControls):
    """Proxy implementation of AbstractSimulatorControls"""

    @property
    def properties(self) -> Union[SimProperties, str]:
        if not self.sim_props:
            sim_props = self._sim_controls.properties
            if not isinstance(sim_props, SimProperties):
                return sim_props
            self.sim_props = sim_props
        return self.sim_props

    def __init__(
        self,
        sim_controls: AbstractSimulatorControls,
        proxy_aircraft_controls: ProxyAircraftControls,
        proxy_waypoint_controls: ProxyWaypointControls,
    ):
        self._sim_controls = sim_controls
        self._proxy_aircraft_controls = proxy_aircraft_controls
        self._proxy_waypoint_controls = proxy_waypoint_controls
        self._logger = logging.getLogger(__name__)
        self.sim_props: Optional[SimProperties] = None
        self._seed = None
        # TODO: Only needs to be enabled if in sandbox mode
        self._timer = Timer(self._log_sim_props, Settings.SIM_LOG_RATE)

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        assert scenario_name, "Must provide a scenario name"
        assert speed >= 0, "Speed must be positive"
        err = self._sim_controls.load_scenario(scenario_name, speed, start_paused)
        if err:
            return err
        # Invalidate all the caches - only on success
        self._clear_caches()
        return None

    def start(self) -> Optional[str]:
        # TODO(RKM 2019-11-19) Start timers?
        return self._sim_controls.start()

    def reset(self) -> Optional[str]:
        err = self._sim_controls.reset()
        if err:
            return err
        self._clear_caches()
        return None

    def pause(self) -> Optional[str]:
        # TODO(RKM 2019-11-19) Pause timers?
        return self._sim_controls.pause()

    def resume(self) -> Optional[str]:
        # TODO(RKM 2019-11-19) Start timers?
        return self._sim_controls.resume()

    def stop(self) -> Optional[str]:
        # TODO(RKM 2019-11-19) Pause timers?
        return self._sim_controls.stop()

    @timeit("ProxySimulatorControls")
    def step(self) -> Optional[str]:
        err = self._sim_controls.step()
        if err:
            return err
        # Will clear, then re-fetch the latest properties
        self._clear_caches()
        self._log_sim_props()
        # TODO(RKM 2019-11-25) Update metrics here (i.e. sector check)
        return None

    def set_speed(self, speed: float) -> Optional[str]:
        assert speed >= 0, "Speed must be positive"
        err = self._sim_controls.set_speed(speed)
        if err:
            return err
        self.sim_props = None
        return None

    def set_seed(self, seed: int) -> Optional[str]:
        assert is_valid_seed(seed), "Invalid seed"
        err = self._sim_controls.set_seed(seed)
        if err:
            return err
        self.sim_props = None
        return None

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        raise NotImplementedError

    def _log_sim_props(self):
        """Logs the current SimProperties"""
        props = self.properties
        if isinstance(props, str):
            self._logger.error(f"Could not get sim properties: {props}")
            return
        data = (
            f"{props.utc_datetime} [{props.scenario_time:4}] "
            f"{props.speed:4}x {props.state.name}"
        )
        self._logger.info(data)

    def _clear_caches(self):
        self.sim_props = None
        self._proxy_aircraft_controls.clear_caches()
        self._proxy_waypoint_controls.waypoints = []
