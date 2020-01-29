"""
Contains the ProxySimulatorControls class
"""
# TODO(rkm 2020-01-22) The startTime and timedelta properties defined in the scenario
# mean that an aircraft may not immediately appear in the data received from the
# simulators. Capture this in AircraftProperties, expose it, and add tests
# TODO(rkm 2020-01-22) Check the effect of loading a new sector when a scenario is
# already running (cached data etc.)
import copy
import json
import logging
from pathlib import Path
from typing import List
from typing import Optional
from typing import Union

import geojson
from aviary.sector.sector_element import SectorElement

from bluebird.settings import Settings
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls
from bluebird.utils.properties import Scenario
from bluebird.utils.properties import Sector
from bluebird.utils.properties import SimProperties
from bluebird.utils.scenario_validation import validate_json_scenario
from bluebird.utils.sector_validation import validate_geojson_sector
from bluebird.utils.timer import Timer
from bluebird.utils.timeutils import timeit


# The rate at which the current sim info is logged to the console (regardless of mode or
# sim speed)
SIM_LOG_RATE = 0.2


class ProxySimulatorControls(AbstractSimulatorControls):
    """Proxy implementation of AbstractSimulatorControls"""

    @property
    def properties(self) -> Union[SimProperties, str]:
        if not self._sim_props or not self._data_valid:
            sim_props = copy.deepcopy(self._sim_controls.properties)
            if not isinstance(sim_props, SimProperties):
                return sim_props
            self._update_sim_props(sim_props)
            self._sim_props = sim_props
            self._data_valid = True
        return self._sim_props

    def __init__(
        self,
        sim_controls: AbstractSimulatorControls,
        proxy_aircraft_controls: ProxyAircraftControls,
    ):
        self._logger = logging.getLogger(__name__)
        self._timer = Timer(self._log_sim_props, SIM_LOG_RATE)
        self._sim_controls = sim_controls
        self._proxy_aircraft_controls = proxy_aircraft_controls
        # NOTE(rkm 2020-01-22) We assume here that the seed is persistent for the
        # current simulation instance, even through calls to load_sector/reset etc.
        self._seed: Optional[int] = None
        self.sector: Optional[Sector] = None
        self._scenario: Optional[Scenario] = None
        self._sim_props: Optional[SimProperties] = None
        self._data_valid: bool = False

    def load_sector(self, sector: Sector) -> Optional[str]:
        """
        Loads the specified sector. If the sector contains an element definition then a
        new sector is created and stored, then uploaded to the simulation. If no sector
        element is defined, then the sector name must refer to an existing sector which
        BlueBird can find (i.e. locally on disk)
        """

        # NOTE(rkm 2020-01-03) We store any new sector (and scenario) definitions
        # locally so they can be loaded again by name at a later point
        loaded_existing_sector = False
        if not sector.element:
            sector_element = self._load_sector_from_file(sector.name)
            if isinstance(sector_element, str):
                return f"Error loading sector from file: {sector_element}"
            sector.element = sector_element
            loaded_existing_sector = True

        err = self._sim_controls.load_sector(sector)
        if err:
            return err

        if not loaded_existing_sector:
            self._save_sector_to_file(sector)

        self._invalidate_data()
        self.sector = sector
        self._scenario = None
        return None

    def load_scenario(self, scenario: Scenario) -> Optional[str]:
        """
        Loads the specified scenario. If the scenario contains content then a new
        scenario is created and stored, then uploaded to the simulation. If the scenario
        only contains a name, then the name must refer to an existing scenario which
        BlueBird can find (i.e. locally on disk)
        """
        if not self.sector:
            return "No sector set"

        loaded_existing_scenario = False
        if not scenario.content:
            scenario_content = self._load_scenario_from_file(scenario.name)
            if isinstance(scenario_content, str):
                return f"Error loading scenario from file: {scenario_content}"
            scenario.content = scenario_content
            loaded_existing_scenario = True

        err = self._validate_scenario_against_sector(
            self.sector.element, scenario.content
        )
        if err:
            return err

        err = self._sim_controls.load_scenario(scenario)
        if err:
            return err

        if not loaded_existing_scenario:
            self._save_scenario_to_file(scenario)

        self._proxy_aircraft_controls.set_initial_properties(
            self.sector.element, scenario.content
        )
        self._invalidate_data()
        self._scenario = scenario
        return None

    def start_timers(self) -> List[Timer]:
        """Start any timed functions, and return all the Timer instances"""
        self._timer.start()
        return [self._timer]

    def start(self) -> Optional[str]:
        return self._invalidating_response(self._sim_controls.start())

    @timeit("ProxySimulatorControls")
    def reset(self) -> Optional[str]:
        err = self._invalidating_response(self._sim_controls.reset(), clear=True)
        if err:
            return err
        self._scenario = None
        return None

    def pause(self) -> Optional[str]:
        return self._invalidating_response(self._sim_controls.pause())

    def resume(self) -> Optional[str]:
        return self._invalidating_response(self._sim_controls.resume())

    def stop(self) -> Optional[str]:
        return self._invalidating_response(self._sim_controls.stop())

    @timeit("ProxySimulatorControls")
    def step(self) -> Optional[str]:
        self._proxy_aircraft_controls.store_current_props()
        return self._invalidating_response(self._sim_controls.step())

    def set_speed(self, speed: float) -> Optional[str]:
        return self._invalidating_response(self._sim_controls.set_speed(speed))

    def set_seed(self, seed: int) -> Optional[str]:
        return self._invalidating_response(self._sim_controls.set_seed(seed))

    def store_data(self) -> Optional[str]:
        """
        Saves the current sector and scenario filenames so they can be easily reloaded.
        This is called last and should therefore be allowed to fail. Re-loading not
        currently implemented :^)
        """
        try:
            if not self.sector:
                self._logger.warning("No sector to store")
                return
            last_sector_file = Settings.DATA_DIR / "sectors" / ".last_sector"
            self._assert_parent_dir_exists(last_sector_file)
            with open(last_sector_file, "w+") as f:
                f.write(self.sector.name + "\n")
            if not self._scenario:
                self._logger.warning("No scenario to store")
                return
            last_scenario_file = Settings.DATA_DIR / "scenarios" / ".last_scenario"
            self._assert_parent_dir_exists(last_scenario_file)
            with open(last_scenario_file, "w+") as f:
                f.write(self._scenario.name + "\n")
        except Exception as exc:
            return f"Error storing data: {exc}"

    def _invalidating_response(
        self, err: Optional[str], clear: bool = False
    ) -> Optional[str]:
        """Utility function which calls _invalidate_data if there is no error"""
        if err:
            return err
        self._invalidate_data(clear=clear)
        return None

    def _log_sim_props(self):
        """Logs the current SimProperties to the console"""
        props = self.properties
        if isinstance(props, str):
            self._logger.error(f"Could not get sim properties: {props}")
            return
        self._logger.info(
            f"UTC={props.utc_datetime}, "
            f"scenario_time={int(props.scenario_time):4}, "
            f"speed={props.speed:.2f}x, "
            f"state={props.state.name}"
        )

    def _invalidate_data(self, clear: bool = False):
        self._proxy_aircraft_controls.invalidate_data(clear=clear)
        self._data_valid = False

    def _update_sim_props(self, sim_props: SimProperties) -> None:
        """Update sim_props with any properties which we manually keep track of"""
        # NOTE(RKM 2020-01-02) When anything we manually set here is changed,
        # _invalidate_data needs to be called
        if self.sector:
            sim_props.sector_name = self.sector.name
        if self._scenario:
            sim_props.scenario_name = self._scenario.name
        sim_props.seed = self._seed

    @staticmethod
    def _sector_filename(sector_name: str) -> Path:
        return Settings.DATA_DIR / "sectors" / f"{sector_name.lower()}.geojson"

    def _load_sector_from_file(self, sector_name: str) -> Union[SectorElement, str]:
        sector_file = self._sector_filename(sector_name)
        self._logger.debug(f"Loading sector from {sector_file}")
        if not sector_file.exists():
            return f"No sector file at {sector_file}"
        with open(sector_file) as f:
            sector_json = json.load(f)
        return validate_geojson_sector(sector_json)

    def _save_sector_to_file(self, sector: Sector):
        sector_file = self._sector_filename(sector.name)
        self._logger.debug(f"Saving sector to {sector_file}")
        if sector_file.exists():
            self._logger.warning("Overwriting existing file")
        self._assert_parent_dir_exists(sector_file)
        with open(sector_file, "w+") as f:
            geojson.dump(sector.element, f, indent=4)

    @staticmethod
    def _scenario_filename(scenario_name: str) -> Path:
        return Settings.DATA_DIR / "scenarios" / f"{scenario_name.lower()}.json"

    def _load_scenario_from_file(self, scenario_name: str) -> Union[str, dict]:
        scenario_file = self._scenario_filename(scenario_name)
        self._logger.debug(f"Loading scenario from {scenario_file}")
        if not scenario_file.exists():
            return f"No scenario file at {scenario_file}"
        with open(scenario_file) as f:
            scenario = json.load(f)
        return validate_json_scenario(scenario) or scenario

    def _save_scenario_to_file(self, scenario: Scenario):
        scenario_file = self._scenario_filename(scenario.name)
        self._logger.debug(f"Saving scenario to {scenario_file}")
        if scenario_file.exists():
            self._logger.warning("Overwriting existing file")
        self._assert_parent_dir_exists(scenario_file)
        with open(scenario_file, "w+") as f:
            json.dump(scenario.content, f, indent=4)

    @staticmethod
    def _assert_parent_dir_exists(file: Path):
        file.parent.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def _validate_scenario_against_sector(sector: SectorElement, scenario: dict):
        """
        Asserts that all waypoints defined in the scenario exist in the current sector
        """
        # TODO(rkm 2020-01-23) Additionally, since the coordinates are repeated in both
        # the sector and scenario definitions, we could also assert that the coordinates
        # for each fix match
        assert sector
        try:
            sector_fixes = list(sector.shape.fixes.keys())
            for aircraft in scenario["aircraft"]:
                for fixName in [x["fixName"] for x in aircraft["route"]]:
                    assert (
                        fixName in sector_fixes
                    ), f"Fix {fixName} not in {sector_fixes}"
        except AssertionError as e:
            return f"Scenario not valid with the current sector: {e}"
