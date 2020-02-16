"""
Contains the AbstractSimulatorControls implementation for MachColl
"""
import logging
import re
import uuid
from datetime import datetime
from datetime import timedelta
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from nats.mc_client.mc_client_metrics import MCClientMetrics

import bluebird.utils.properties as props
from bluebird.metrics.abstract_metrics_provider import AbstractMetricsProvider
from bluebird.settings import Settings
from bluebird.sim_client.machcoll.machcoll_aircraft_controls import (
    MachCollAircraftControls,
)
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls


class MachCollSimulatorControls(AbstractSimulatorControls):
    """AbstractSimulatorControls implementation for MachColl"""

    def __init__(
        self,
        sim_client,
        aircraft_controls: MachCollAircraftControls,
        mc_metrics_provider: AbstractMetricsProvider,
    ):
        self._sim_client = sim_client
        self._aircraft_controls = aircraft_controls
        self._mc_metrics_provider = mc_metrics_provider
        assert str(self._mc_metrics_provider) == "MachColl"
        self._registered_metrics: List[str] = list(self._mc_metrics_provider.metrics)
        self._logger = logging.getLogger(__name__)
        self._scenario_start_time = 0

    @property
    def properties(self) -> Union[props.SimProperties, str]:

        sim_state = self._get_sim_state()
        if not isinstance(sim_state, props.SimState):
            return sim_state

        sim_speed = self._mc_client().get_speed()
        self._raise_for_no_data(sim_speed)
        if not isinstance(sim_speed, (float, int)):
            return sim_speed

        times = self._get_sim_times()
        if not isinstance(times, tuple):
            return times
        scenario_time, utc_datetime = times

        return props.SimProperties(
            dt=0,  # TODO(rkm 2020-01-31) Currently unknown
            scenario_name=None,
            scenario_time=scenario_time,
            sector_name=None,
            seed=None,
            speed=sim_speed,
            state=sim_state,
            utc_datetime=utc_datetime,
        )

    def load_sector(self, sector: props.Sector) -> Optional[str]:
        assert sector.element, "Expected sector element to be set"
        sector_filename = f"{sector.name}.geojson"
        source_sector_path = Settings.DATA_DIR / "sectors" / sector_filename
        assert source_sector_path.exists(), f"Expected that {source_sector_path} exists"

        # TODO(rkm 2020-02-02) Temp. Currently can't replace existing files
        uuid_str = str(uuid.uuid1())[:4]
        sector_filename = f"{sector.name}-{uuid_str}.geojson"

        # First upload the sector
        uploaded_filename = self._mc_client().upload_airspace_file(
            source_sector_path, sector_filename
        )
        self._logger.debug(
            f"{uploaded_filename} <- upload_airspace_file("
            f"{source_sector_path}, {sector_filename})"
        )
        self._raise_for_no_data(uploaded_filename)
        if not isinstance(uploaded_filename, str):
            return str(uploaded_filename)

        # Now load it by name
        loaded_sector = self._mc_client().set_airspace_file(uploaded_filename)
        self._logger.debug(f"{loaded_sector} <- set_airspace_file({uploaded_filename})")
        self._raise_for_no_data(loaded_sector)
        return (
            None
            if isinstance(loaded_sector, str)
            else f"Unsuccessful call to set_airspace_file: {loaded_sector}"
        )

    def load_scenario(self, scenario: props.Scenario) -> Optional[str]:
        assert scenario.content, "Expected scenario content to be populated"
        scenario_filename = f"{scenario.name}.json"
        source_scenario_path = Settings.DATA_DIR / "scenarios" / scenario_filename
        assert (
            source_scenario_path.exists()
        ), f"Expected that {source_scenario_path} exists"

        # TODO(rkm 2020-02-02) Temp. Currently can't replace existing files
        uuid_str = str(uuid.uuid1())[:4]
        scenario_filename = f"{scenario.name}-{uuid_str}.json"

        # First upload the scenario
        uploaded_filename = self._mc_client().upload_scenario_file(
            source_scenario_path, scenario_filename
        )
        self._logger.debug(
            f"{uploaded_filename} <- upload_scenario_file("
            f"{source_scenario_path}, {scenario_filename})"
        )
        if not isinstance(uploaded_filename, str):
            return str(uploaded_filename)

        # Now load it by name
        loaded_scenario = self._mc_client().set_scenario_filename(uploaded_filename)
        self._raise_for_no_data(loaded_scenario)
        if not isinstance(loaded_scenario, str):
            return f'Unsuccessful call to set_scenario_filename: "{loaded_scenario}"'
        self._scenario_start_time = self._parse_start_time(scenario.content)
        return None

    # TODO Assert state is as expected after all of these methods (should be in the
    # response)
    def start(self) -> Optional[str]:
        # NOTE: If agent mode, no need to explicitly start since we can step from init
        state = self._get_sim_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.RUN:
            return
        resp = self._mc_client().sim_start()
        self._raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def reset(self) -> Optional[str]:
        state = self._get_sim_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.INIT:
            return
        resp = self._mc_client().sim_stop()
        self._raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def pause(self) -> Optional[str]:
        state = self._get_sim_state()
        if isinstance(state, str):
            return state
        if state in [
            props.SimState.INIT,
            props.SimState.HOLD,
            props.SimState.END,
        ]:
            return None
        resp = self._mc_client().sim_pause()
        self._raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def resume(self) -> Optional[str]:
        state = self._get_sim_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.RUN:
            return None
        if state == props.SimState.END:
            return "Can't resume sim from 'END' state"
        resp = self._mc_client().sim_resume()
        self._raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def stop(self) -> Optional[str]:
        state = self._get_sim_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.END:
            return
        resp = self._mc_client().sim_stop()
        self._raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def step(self) -> Optional[str]:
        self._mc_client().queue_metrics_query("metrics.score")
        resp = self._mc_client().set_increment()
        self._raise_for_no_data(resp)
        self._mc_metrics_provider.update(self._mc_client().get_metrics_result())
        return None if self._is_success(resp) else str(resp)

    def set_speed(self, speed: float) -> Optional[str]:
        resp = (
            self._mc_client().set_step(speed)
            if Settings.SIM_MODE == props.SimMode.Agent
            else self._mc_client().set_speed(speed)
        )
        self._raise_for_no_data(resp)
        self._logger.warning(f"Unhandled data: {resp}")
        return None if (resp == speed) else f"Unknown response: {resp}"

    def set_seed(self, seed: int) -> Optional[str]:
        return "Not implemented"

    def _mc_client(self) -> MCClientMetrics:
        return self._sim_client.mc_client

    def _get_sim_state(self) -> Union[props.SimState, str]:
        # TODO There is also a possible "stepping" mode (?)
        resp = self._mc_client().get_state()
        if not resp:
            return "Could not get state - no response received"
        if resp.upper() == "INIT":
            return props.SimState.INIT
        if resp.upper() == "RUNNING":
            return props.SimState.RUN
        if resp.upper() == "STOPPED":
            return props.SimState.END
        if resp.upper() == "PAUSED":
            return props.SimState.HOLD
        return f"Could not parse a valid sim state value from {resp}"

    def _get_sim_times(self) -> Union[Tuple[Union[float, int], datetime], str]:
        resp = self._mc_client().get_time()
        if not isinstance(resp, (float, int)):
            return resp
        utc_datetime = (
            datetime.combine(datetime.today(), datetime.min.time())
            + timedelta(seconds=resp)
        ).strftime("%Y-%m-%d %H:%M:%S")
        scenario_time = resp - self._scenario_start_time
        return (scenario_time, utc_datetime)

    @staticmethod
    def _is_success(data) -> bool:
        try:
            return data["code"]["Short Description"] == "Success"
        except KeyError:
            pass
        return False

    @staticmethod
    def _raise_for_no_data(data) -> None:
        assert data is not None, "No data received from the simulator"

    def _parse_start_time(self, data) -> int:
        start_time = data.get("startTime", None)
        if start_time is None:
            self._logger.warning("Start time not found in data")
            return 0
        # NOTE(rkm 2020-02-02) Assuming a simple "HH:MM:SS" format
        assert re.match(r"\d{2}:\d{2}:\d{2}", start_time)
        return sum(x * int(t) for x, t in zip([3600, 60, 1], start_time.split(":")))
