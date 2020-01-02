"""
Contains the AbstractSimulatorControls implementation for BlueSky
"""

import logging
import traceback
from datetime import datetime
from typing import Iterable
from typing import Optional
from typing import Union

import bluebird.utils.properties as props
from bluebird.settings import in_agent_mode
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
        self._seed = None
        self._dt_mult: float = 1.0

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ) -> Optional[str]:
        assert scenario_name
        return self._bluesky_client.load_scenario(scenario_name, speed, start_paused)

    def start(self) -> Optional[str]:
        return self._bluesky_client.send_stack_cmd("OP")

    def reset(self) -> Optional[str]:
        self._dt_mult = 1
        return self._bluesky_client.reset_sim()

    def pause(self) -> Optional[str]:
        return self._bluesky_client.send_stack_cmd("HOLD")

    def resume(self) -> Optional[str]:
        return self._bluesky_client.send_stack_cmd("OP")

    def stop(self) -> Optional[str]:
        return self._bluesky_client.send_stack_cmd("STOP")

    def step(self) -> Optional[str]:
        return self._bluesky_client.step()

    def set_speed(self, speed: float) -> Optional[str]:
        if not in_agent_mode():
            return self._bluesky_client.send_stack_cmd(f"DT {speed}")
        resp = self._bluesky_client.send_stack_cmd(
            f"DTMULT {speed}", response_expected=True
        )
        err = self._check_expected_resp(resp)
        if err:
            return err
        self._dt_mult = speed
        return None

    def upload_new_scenario(
        self, scn_name: str, content: Iterable[str]
    ) -> Optional[str]:
        return self._bluesky_client.upload_new_scenario(scn_name, content)

    def set_seed(self, seed: int) -> Optional[str]:
        resp = self._bluesky_client.send_stack_cmd(
            f"SEED {seed}", response_expected=True
        )
        err = self._check_expected_resp(resp)
        if err:
            return err
        self._seed = int(resp[0].split(" ")[-1])
        return None

    def _check_expected_resp(self, resp) -> Optional[str]:
        if not isinstance(resp, list) and len(resp) == 1 and "set to" not in resp[0]:
            return f'No confirmation received from BlueSky. Received: "{resp}"'
        return None

    def _convert_to_sim_props(self, data: tuple) -> Union[props.SimProperties, str]:
        try:
            return props.SimProperties(
                sector_name=None,
                scenario_name=data[6],
                scenario_time=round(data[2], 2),
                seed=self._seed,
                speed=self._dt_mult if in_agent_mode() else round(data[0], 2),
                state=self._parse_sim_state(data[5]),
                dt=data[1],
                utc_datetime=datetime.strptime(data[3], "%Y-%m-%d %H:%M:%S"),
            )
        except Exception:
            return (
                f"Error converting stream data to sim properties: "
                f"{traceback.format_exc()}"
            )
