"""
Contains the ProxySimulatorControls class
"""

import logging
from dataclasses import dataclass
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

from aviary.sector.sector_element import SectorElement

from bluebird.settings import in_agent_mode
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls
from bluebird.utils.properties import SimProperties
from bluebird.utils.properties import Scenario
from bluebird.utils.timer import Timer
from bluebird.utils.timeutils import timeit
from bluebird.utils.types import is_valid_seed


# The rate at which the current sim info is logged to the console (regardless of mode or
# sim speed)
SIM_LOG_RATE = 0.2


@dataclass
class Sector:
    name: str
    element: SectorElement


class ProxySimulatorControls(AbstractSimulatorControls):
    """Proxy implementation of AbstractSimulatorControls"""

    @property
    def sector(self) -> Sector:
        return self._sector

    @property
    def properties(self) -> Union[SimProperties, str]:
        if not in_agent_mode():
            return self._sim_controls.properties
        if not self._sim_props:
            sim_props = self._sim_controls.properties
            if not isinstance(sim_props, SimProperties):
                return sim_props
            self._sim_props = self._update_sim_props(sim_props)
        return self._sim_props

    def __init__(
        self,
        sim_controls: AbstractSimulatorControls,
        clear_cache_functions: List[Callable],
    ):
        self._logger = logging.getLogger(__name__)
        self._timer = Timer(self._log_sim_props, SIM_LOG_RATE)
        self._sim_controls = sim_controls
        self._clear_cache_functions = clear_cache_functions
        self._seed: Optional[int] = None
        self._sector: Optional[Sector] = None

        # Only store a cache of the sim properties if we are in agent mode
        if in_agent_mode():
            self._sim_props: Optional[SimProperties] = None

    def load_scenario(self, scenario: Scenario) -> Optional[str]:
        err = self._sim_controls.load_scenario(scenario)
        if err:
            return err
        self._clear_caches()
        return None

    def start_timers(self) -> List[Timer]:
        return [self._timer.start()]

    def start(self) -> Optional[str]:
        return self._sim_controls.start()

    def reset(self) -> Optional[str]:
        err = self._sim_controls.reset()
        if err:
            return err
        self._clear_caches()
        return None

    def pause(self) -> Optional[str]:
        return self._sim_controls.pause()

    def resume(self) -> Optional[str]:
        return self._sim_controls.resume()

    def stop(self) -> Optional[str]:
        return self._sim_controls.stop()

    @timeit("ProxySimulatorControls")
    def step(self) -> Optional[str]:
        err = self._sim_controls.step()
        if err:
            return err
        self._clear_caches()
        # TODO(RKM 2019-11-25) Update metrics here (i.e. sector check)
        return None

    def set_speed(self, speed: float) -> Optional[str]:
        assert speed >= 0, "Speed must be positive"
        return self._sim_controls.set_speed(speed)

    def set_seed(self, seed: int) -> Optional[str]:
        assert is_valid_seed(seed), "Invalid seed"
        err = self._sim_controls.set_seed(seed)
        if err:
            return err
        self._clear_caches()
        return None

    def set_sector(self, sector: Sector) -> Optional[str]:
        """Updates the current sector and sends it to the sim"""
        self._sector = sector
        # TODO(RKM 2019-12-20) Update the sim
        # TODO(RKM 2019-12-28) Write to disk / touch on exit
        self._clear_caches()

    def _log_sim_props(self):
        """Logs the current SimProperties to the console"""
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
        if in_agent_mode():
            self._sim_props = None
            for func in self._clear_cache_functions:
                func()

    def _update_sim_props(self, sim_props: SimProperties) -> SimProperties:
        """Update sim_props with any properties which we manually keep track of"""
        # NOTE(RKM 2020-01-02) When anything we manually set here is changed,
        # _clear_cache needs to be called
        if self._sector:
            sim_props.sector_name = self._sector.name
        sim_props.seed = self._seed
        return sim_props
