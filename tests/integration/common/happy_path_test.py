"""
Basic "happy path" test for any simulator
"""
# NOTE(RKM 2020-01-01) Note that this test isn't run directly, but is imported and
# called by the tests for each simulator
from dataclasses import dataclass
from datetime import datetime
from http import HTTPStatus
from typing import Any
from typing import Dict

import requests

import tests.integration
from tests.data import TEST_SCENARIO
from tests.data import TEST_SECTOR


@dataclass
class SimUniqueProps:
    """Represents any differences in the sim properties for a given simulator type"""

    # TODO: Metrics providers
    sim_type: str
    dt: float
    initial_utc_datetime: datetime


def _get_sim_info(api_base: str) -> Dict[str, Any]:
    resp = requests.get(f"{api_base}/siminfo")
    assert resp.status_code == HTTPStatus.OK
    return resp.json()


def run_happy_path(props: SimUniqueProps):
    """Runs though a basic scenario covering all the main API functionality"""

    api_base = tests.integration.API_BASE

    resp = requests.post(f"{api_base}/reset")
    assert resp.status_code == 200

    assert _get_sim_info(api_base) == {
        "callsigns": [],
        "dt": props.dt,
        "mode": "Agent",
        "scenario_name": None,
        "scenario_time": 0.0,
        "sector_name": None,
        "seed": None,
        "sim_type": props.sim_type,
        "speed": 1,  # NOTE This is the DTMULT value in agent mode
        "state": "INIT",
        "utc_datetime": str(props.initial_utc_datetime),
    }

    data = {"name": "sector-1", "content": TEST_SECTOR}
    resp = requests.post(f"{api_base}/sector", json=data)
    assert resp.status_code == HTTPStatus.CREATED

    sim_info = _get_sim_info(api_base)
    assert sim_info["sector_name"] == "sector-1"

    data = {"name": "scenario-1", "content": TEST_SCENARIO}
    resp = requests.post(f"{api_base}/scenario", json=data)
    assert resp.status_code == HTTPStatus.CREATED

    sim_info = _get_sim_info(api_base)
    assert sim_info["callsigns"] == [x["callsign"] for x in TEST_SCENARIO["aircraft"]]
    assert sim_info["scenario_name"] == "scenario-1"

    # TODO
    # Set the step size
    # Perform a step
    # Get the positions
    # Issue an altitude command
    # Perform a step
    # Get the positions
    # Get the metrics
    # Perform a step
    # Get the metrics
