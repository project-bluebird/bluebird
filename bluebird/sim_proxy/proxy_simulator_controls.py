"""
Contains the ProxySimulatorControls class
"""

import json
import logging
from typing import Callable
from typing import List
from typing import Optional
from typing import Union

from bluebird.settings import in_agent_mode
from bluebird.settings import Settings
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls
from bluebird.utils.properties import Scenario
from bluebird.utils.properties import Sector
from bluebird.utils.properties import SimProperties
from bluebird.utils.sector_validation import validate_geojson_sector
from bluebird.utils.timer import Timer
from bluebird.utils.timeutils import timeit
from bluebird.utils.types import is_valid_seed


# The rate at which the current sim info is logged to the console (regardless of mode or
# sim speed)
SIM_LOG_RATE = 0.2


class ProxySimulatorControls(AbstractSimulatorControls):
    """Proxy implementation of AbstractSimulatorControls"""

    @property
    def sector(self) -> Optional[Sector]:
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
        self._props_logger = logging.getLogger(__name__)
        self._props_logger.name = "Sim Info"

        self._timer = Timer(self._log_sim_props, SIM_LOG_RATE)
        self._sim_controls = sim_controls
        self._clear_cache_functions = clear_cache_functions
        self._seed: Optional[int] = None
        self._sector: Optional[Sector] = None

        # Only store a cache of the sim properties if we are in agent mode
        if in_agent_mode():
            self._sim_props: Optional[SimProperties] = None

    def load_sector(self, sector: Sector) -> Optional[str]:
        """
        Loads the specified sector. If the sector contains an element definition then a
        new sector is created and stored, then uploaded to the simulation. If no sector
        element is defined, then the sector name must refer to an existing sector which
        BlueBird can find (i.e. locally on disk)
        """

        # NOTE(rkm 2020-01-03) We can't currently read the current sector definition
        # from either simulator, so we can only check if we have it locally
        if not sector.element:
            sector_element = self._load_sector_from_file()
            if isinstance(sector_element, str):
                return f"Error loading sector from file: {sector_element}"
            sector.element = sector_element

        err = self._sim_controls.load_sector(sector)
        if err:
            return err

        self._save_sector_to_file(sector)
        self._sector = sector
        self._clear_caches()
        return None

    def load_scenario(self, scenario: Scenario) -> Optional[str]:
        err = self._sim_controls.load_scenario(scenario)
        if err:
            return err
        self._clear_caches()
        return None

    def start_timers(self) -> List[Timer]:
        """Start any timed functions, and return all the Timer instances"""
        self._timer.start()
        return [self._timer]

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

    def _log_sim_props(self):
        """Logs the current SimProperties to the console"""
        props = self.properties
        if isinstance(props, str):
            self._logger.error(f"Could not get sim properties: {props}")
            return
        self._props_logger.info(
            f"UTC={props.utc_datetime}, "
            f"scenario_time={int(props.scenario_time):4}, "
            f"speed={props.speed:4}x, "
            f"scenario={props.state.name}"
        )

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

    def _load_sector_from_file(self, sector: Sector):
        sector_file = Settings.DATA_DIR / "sectors" / f"{sector.name}.geojson"
        self._logger.debug(f"Loading sector from {sector_file}")
        if not sector_file.exists():
            return f"No sector file at {sector_file}"
        with open(sector_file, "r") as f:
            return validate_geojson_sector(json.load(f))

    def _save_sector_to_file(self, sector: Sector):
        sector_file = Settings.DATA_DIR / "sectors" / f"{sector.name}.geojson"
        self._logger.debug(f"Saving sector to {sector_file}")
        if sector_file.exists():
            self._logger.warning("Overwriting existing file")
        sector_file.parent.mkdir(parents=True, exist_ok=True)
        with open(sector_file, "w+") as f:
            json.dump(sector.element.sector_geojson(), f)
