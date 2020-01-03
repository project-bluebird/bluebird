"""
Contains the AbstractSimulatorControls implementation for BlueSky
"""

import logging
import traceback
from datetime import datetime
from typing import Any
from typing import List
from typing import Optional
from typing import Union

from aviary.parser.bluesky_parser import BlueskyParser

import bluebird.utils.properties as props
from bluebird.settings import in_agent_mode
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls
from bluebird.utils.properties import Scenario


# From bluesky/bluesky/__init__.py
_BS_STATE_MAP = [
    props.SimState.INIT,
    props.SimState.HOLD,
    props.SimState.RUN,
    props.SimState.END,
]


class BlueSkySimulatorControls(AbstractSimulatorControls):
    """AbstractSimulatorControls implementation for BlueSky"""

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
        self._dt_mult: float = 1.0
        self._sector: Optional[props.Sector] = None

    def load_sector(self, sector: props.Sector) -> Optional[str]:
        # NOTE(rkm 2020-01-03) This function is a no-op for BlueSky, since it doesn't
        # have separate concepts of sectors and scenarios. We only store the sector so
        # we can use it in load_scenario
        assert sector.element
        self._sector = sector

    def load_scenario(self, scenario: Scenario) -> Optional[str]:
        file_name = f"{scenario.name}.scn".lower()
        if not scenario.content:
            return self._bluesky_client.load_scenario(file_name, in_agent_mode())

        assert self._sector
        try:
            # TODO(rkm 2020-01-03) What exceptions can this raise?
            # NOTE Errors here (aviary parsing) may be caused by error in the previously
            # stored sector definition
            parser = BlueskyParser(self._sector.element, scenario.content)
            scenario_lines = parser.all_lines()
        except Exception as e:
            return f"Could not parse a BlueSky scenario: {e}"
        err = self._bluesky_client.upload_new_scenario(file_name, scenario_lines)
        if err:
            return err
        return self._bluesky_client.load_scenario(file_name)

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
        resp = self._bluesky_client.send_stack_cmd(
            f"DTMULT {speed}", response_expected=True
        )
        err = self._check_expected_resp(resp)
        if err:
            return err
        self._dt_mult = speed
        return None

    def set_seed(self, seed: int) -> Optional[str]:
        resp = self._bluesky_client.send_stack_cmd(
            f"SEED {seed}", response_expected=True
        )
        err = self._check_expected_resp(resp)
        if err:
            return err
        return None

    def _check_expected_resp(self, resp) -> Optional[str]:
        if isinstance(resp, list) and len(resp) == 1 and "set to" in resp[0]:
            return None
        return f'No confirmation received from BlueSky. Received: "{resp}"'

    def _convert_to_sim_props(self, data: List[Any]) -> Union[props.SimProperties, str]:
        try:
            return props.SimProperties(
                sector_name=None,
                scenario_name=data[6],
                scenario_time=round(data[2], 2),
                seed=None,
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
