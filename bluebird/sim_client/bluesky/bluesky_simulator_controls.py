"""
Contains the AbstractSimulatorControls implementation for BlueSky
"""

import logging
import traceback
from typing import Iterable, Optional, Union

import bluebird.utils.properties as props
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls


# From bluesky/bluesky/__init__.py
_BS_STATE_MAP = [
    props.SimState.INIT,
    props.SimState.HOLD,
    props.SimState.RUN,
    props.SimState.END,
]


class BlueSkySimulatorControls(AbstractSimulatorControls):
    """
    AbstractSimulatorControls implementation for BlueSky
    """

    @staticmethod
    def _parse_sim_state(val: int) -> props.SimState:
        assert 0 <= val < len(_BS_STATE_MAP)
        return _BS_STATE_MAP[val]

    @property
    def properties(self) -> Union[props.SimProperties, str]:
        data = self._bluesky_client.sim_info_stream_data
        return self._convert_to_sim_props(data)

    def __init__(self, bluesky_client):
        self._bluesky_client = bluesky_client
        self._logger = logging.getLogger(__name__)

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        assert scenario_name
        return self._bluesky_client.load_scenario(scenario_name, speed, start_paused)

    def start(self) -> Optional[str]:
        raise NotImplementedError

    def reset(self) -> Optional[str]:
        return self._bluesky_client.reset_sim()

    def pause(self) -> Optional[str]:
        raise NotImplementedError

    def resume(self) -> Optional[str]:
        raise NotImplementedError

    def stop(self) -> Optional[str]:
        raise NotImplementedError

    def step(self) -> Optional[str]:
        return self._bluesky_client.step()

    def set_speed(self, speed: float) -> Optional[str]:
        raise NotImplementedError

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        raise NotImplementedError

    def set_seed(self, seed: int) -> Optional[str]:
        raise NotImplementedError

    def _convert_to_sim_props(self, data: tuple) -> Union[props.SimProperties, str]:
        try:
            sim_props = props.SimProperties(
                scenario_name=data[6],
                scenario_time=round(data[2], 2),
                seed=None,  # TODO
                speed=round(data[0], 2),
                state=self._parse_sim_state(data[5]),
                step_size=data[1],
                utc_time=data[3],  # TODO
            )
            self._logger.info(f"Given UTC: {data[3]}")
            self._logger.info(f"Parsed UTC: {sim_props.utc_time}")
            return sim_props
        except Exception:
            return (
                f"Error converting stream data to sim properties: "
                f"{traceback.format_exc()}"
            )
