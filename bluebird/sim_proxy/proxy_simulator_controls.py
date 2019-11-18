"""
Contains the ProxySimulatorControls class
"""

import logging

from typing import Optional, Union, Iterable

from bluebird.settings import Settings
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls
from bluebird.utils.properties import SimProperties, SimState
from bluebird.utils.timer import Timer


class ProxySimulatorControls(AbstractSimulatorControls):
    """Proxy implementation of AbstractSimulatorControls"""

    @property
    def stream_data(self) -> SimProperties:
        raise NotImplementedError

    @property
    def properties(self) -> Union[SimProperties, str]:
        raise NotImplementedError

    # @property
    # def time(self) -> Union[float, str]:
    #     raise NotImplementedError

    def __init__(self, sim_controls: AbstractSimulatorControls):
        self._logger = logging.getLogger(__name__)
        self._sim_controls = sim_controls
        # TODO: Only needs to be enabled if in sandbox mode
        self._timer = Timer(self.log_sim_props, Settings.SIM_LOG_RATE)

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        raise NotImplementedError

    def start(self) -> Optional[str]:
        raise NotImplementedError

    def reset(self) -> Optional[str]:
        # TODO(RKM 2019-11-18) What else to do before issuing reset(?)
        return self._sim_controls.reset()

    def pause(self) -> Optional[str]:
        raise NotImplementedError

    def resume(self) -> Optional[str]:
        raise NotImplementedError

    def stop(self) -> Optional[str]:
        raise NotImplementedError

    @staticmethod
    def parse_sim_state(val: str) -> Union[SimState, str]:
        raise NotImplementedError

    def step(self) -> Optional[str]:
        raise NotImplementedError

    def get_speed(self) -> Union[float, str]:
        raise NotImplementedError

    def set_speed(self, speed: float) -> Optional[str]:
        raise NotImplementedError

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        raise NotImplementedError

    def get_seed(self) -> int:
        raise NotImplementedError

    def set_seed(self, seed: int) -> Optional[str]:
        raise NotImplementedError

    def log_sim_props(self):
        """Logs the current SimProperties"""
        props = self.properties
        if isinstance(props, str):
            self._logger.error(f"Could not get sim properties: {props}")
            return
        data = (
            f"speed={props.speed}x, ticks={props.scenario_time:4}, "
            f"time={props.utc_time}, state={props.state.name}"
        )
        self._logger.info(data)
