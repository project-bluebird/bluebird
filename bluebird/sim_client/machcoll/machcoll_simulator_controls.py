"""
Contains the AbstractSimulatorControls implementation for MachColl
"""
import json
import logging
import tempfile
from datetime import datetime
from datetime import timedelta
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


def _raise_for_no_data(data):
    assert data, "No data received from the simulator"


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
        self._logger = logging.getLogger(__name__)

    @property
    def properties(self) -> Union[props.SimProperties, str]:

        sim_state = self._get_sim_state()
        if not isinstance(sim_state, props.SimState):
            return sim_state

        sim_speed = self._mc_client().get_speed()
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
        assert sector.element
        file_name = f"{sector.name}.geojon"
        with tempfile.NamedTemporaryFile() as tf:
            json.dump(sector.element.sector_geojson(), tf)
            resp = self._mc_client().upload_airspace_file(tf, file_name)
        return None if resp == file_name else f'Unsuccessful upload: "{resp}"'

    def load_scenario(self, scenario: props.Scenario) -> Optional[str]:
        file_name = f"{scenario.name}.json"
        if scenario.content:
            with tempfile.NamedTemporaryFile() as tf:
                json.dump(scenario.content, tf)
                resp = self._mc_client().upload_scenario_file(tf, file_name)
            if not resp == file_name:
                return f'Unsuccessful upload: "{resp}"'
        resp = self._mc_client().set_scenario_filename(file_name)
        return None if resp == file_name else f'Unsuccessful request: "{resp}"'

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
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def reset(self) -> Optional[str]:
        state = self._get_sim_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.INIT:
            return
        resp = self._mc_client().sim_stop()
        _raise_for_no_data(resp)
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
        _raise_for_no_data(resp)
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
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def stop(self) -> Optional[str]:
        state = self._get_sim_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.END:
            return
        resp = self._mc_client().sim_stop()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def step(self) -> Optional[str]:
        # TODO(RKM 2019-11-24) get the list of metrics to queue, and their args(?)
        # self._mc_client().queue_metrics_query("metrics.score")
        resp = self._mc_client().set_increment()
        _raise_for_no_data(resp)
        self._aircraft_controls.clear_cache()  # TODO
        # TODO(RKM 2019-11-26) Update metrics
        # self._mc_metrics_provider.update(...)
        return None if self._is_success(resp) else str(resp)

    def set_speed(self, speed: float) -> Optional[str]:
        resp = (
            self._mc_client().set_step(speed)
            if Settings.SIM_MODE == props.SimMode.Agent
            else self._mc_client().set_speed(speed)
        )
        _raise_for_no_data(resp)
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
        scenario_time = resp - 46_800  # 13 hours in seconds
        return (scenario_time, utc_datetime)

    @staticmethod
    def _is_success(data) -> bool:
        try:
            return data["code"]["Short Description"] == "Success"
        except KeyError:
            pass
        return False
