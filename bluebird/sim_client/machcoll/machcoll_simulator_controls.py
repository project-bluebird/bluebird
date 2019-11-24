"""
Contains the AbstractSimulatorControls implementation for MachColl
"""

import logging
import traceback
from typing import Optional, Union, Iterable

import bluebird.utils.properties as props
from bluebird.sim_client.machcoll.machcoll_client_imports import MCClientMetrics
from bluebird.settings import Settings
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls


def _raise_for_no_data(data):
    assert data, "No data received from the simulator"


class MachCollSimulatorControls(AbstractSimulatorControls):
    """
    AbstractSimulatorControls implementation for MachColl
    """

    # @property
    # def stream_data(self) -> Optional[bb_props.SimProperties]:
    #     raise NotImplementedError

    @property
    def properties(self) -> Union[props.SimProperties, str]:
        responses = []
        for req in [
            self._mc_client().get_state,
            self._mc_client().get_speed,
            self._mc_client().get_step,
            self._mc_client().get_time,
        ]:
            responses.append(req())
            if not responses[-1]:
                return f"Could not get property from sim ({req.__name__})"

        try:
            responses[0] = self._parse_sim_state(responses[0])
        except ValueError:
            return traceback.format_exc()

        # Different type returned on failure, have to handle separately
        responses.append(self._mc_client().get_scenario_filename())
        if not isinstance(responses[-1], str):
            return f"Could not get the current scenario name: {responses[-1]}"

        try:
            assert len(responses) == len(
                props.SimProperties.__annotations__
            ), "Expected the number of arguments to match"
            return props.SimProperties(*responses)  # Splat!
        except AssertionError:
            return traceback.format_exc()

    def __init__(self, mc_client: MCClientMetrics):
        self._mc_client = mc_client
        self._logger = logging.getLogger(__name__)

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        self._logger.debug(f"Loading {scenario_name}")
        self._logger.warning(f"Unhandled arguments: speed, start_paused")
        resp = self._mc_client().set_scenario_filename(scenario_name)
        # TODO Check this is as expected. MCClient docstring suggests that an error
        # response will be returned on failure, however currently None is returned on
        # failure and the scenario name is passed back on success
        if not resp:
            return "Error: No confirmation received from MachColl"
        return None

    # TODO Assert state is as expected after all of these methods (should be in the
    # response)
    def start(self) -> Optional[str]:
        # NOTE: If agent mode, no need to explicitly start since we can step from init
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.RUN:
            return
        resp = self._mc_client().sim_start()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def reset(self) -> Optional[str]:
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.INIT:
            return
        resp = self._mc_client().sim_stop()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def pause(self) -> Optional[str]:
        state = self._get_state()
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
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.RUN:
            return None
        if state == props.SimState.END:
            return 'Can\'t resume sim from "END" state'
        resp = self._mc_client().sim_resume()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def stop(self) -> Optional[str]:
        state = self._get_state()
        if isinstance(state, str):
            return state
        if state == props.SimState.END:
            return
        resp = self._mc_client().sim_stop()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    def step(self) -> Optional[str]:
        # TODO: Work-in the other metrics. Do we want to get every metric at every step?
        self._mc_client().queue_metrics_query("metrics.score")
        resp = self._mc_client().set_increment()
        _raise_for_no_data(resp)
        return None if self._is_success(resp) else str(resp)

    # def get_speed(self) -> float:
    #     resp = (
    #         self._mc_client().get_step()
    #         if Settings.SIM_MODE == bb_props.SimMode.Agent
    #         else self._mc_client().get_speed()
    #     )
    #     _raise_for_no_data(resp)
    #     _LOGGER.warning(f"Unhandled data: {resp}")
    #     return -1

    def set_speed(self, speed: float) -> Optional[str]:
        resp = (
            self._mc_client().set_step(speed)
            if Settings.SIM_MODE == props.SimMode.Agent
            else self._mc_client().set_speed(speed)
        )
        _raise_for_no_data(resp)
        self._logger.warning(f"Unhandled data: {resp}")
        return None if (resp == speed) else f"Unknown response: {resp}"

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        raise NotImplementedError

    # def get_seed(self) -> int:
    #     raise NotImplementedError

    def set_seed(self, seed: int) -> Optional[str]:
        # NOTE: There is a function in McClient for this, but it isn't implemented there
        # yet
        raise NotImplementedError

    @staticmethod
    def _parse_sim_state(val: str) -> props.SimState:
        # TODO There is also a possible "stepping" mode (?)
        if val.upper() == "INIT":
            return props.SimState.INIT
        if val.upper() == "RUNNING":
            return props.SimState.RUN
        if val.upper() == "STOPPED":
            return props.SimState.END
        if val.upper() == "PAUSED":
            return props.SimState.HOLD
        raise ValueError(f'Unknown state: "{val}"')

    def _mc_client(self) -> MCClientMetrics:
        return self._sim_client.mc_client

    def _get_state(self) -> Union[props.SimState, str]:
        state = self._mc_client().get_state()
        if not state:
            return f"Could not get the sim state"
        try:
            return self._parse_sim_state(state)
        except ValueError as exc:
            return f"Error getting sim state: {exc}"

    @staticmethod
    def _is_success(data) -> bool:
        try:
            return data["code"]["Short Description"] == "Success"
        except KeyError:
            pass
        return False
