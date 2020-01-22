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
from tests.data import TEST_SECTOR


@dataclass
class SimUniqueProps:
    # TODO: Metrics providers
    sim_type: str
    dt: float
    initial_utc_datetime: datetime


def get_sim_info(api_base: str) -> Dict[str, Any]:
    resp = requests.get(f"{api_base}/siminfo")
    assert resp.status_code == HTTPStatus.OK
    return resp.json()


def run_happy_path(props: SimUniqueProps):
    """Runs though a basic scenario covering all the main API functionality"""

    api_base = tests.integration.API_BASE

    resp = requests.post(f"{api_base}/reset")
    assert resp.status_code == 200

    sim_info = get_sim_info(api_base)
    assert sim_info["callsigns"] == []
    assert sim_info["mode"] == "Agent"
    assert sim_info["scenario_name"] is None
    assert sim_info["scenario_time"] == 0
    assert sim_info["seed"] is None
    assert sim_info["sim_type"].lower() == props.sim_type
    assert sim_info["speed"] == 1  # NOTE This is the DTMULT value in agent mode
    assert sim_info["state"] == "INIT"
    assert sim_info["dt"] == props.dt
    assert sim_info["utc_datetime"] == str(props.initial_utc_datetime)

    data = {"name": "sector-1", "content": TEST_SECTOR}
    resp = requests.post(f"{api_base}/sector", json=data)
    assert resp.status_code == HTTPStatus.CREATED

    sim_info = get_sim_info(api_base)
    assert sim_info["sector_name"] == "sector-1"

    # TODO
    # Load a scenario
    # Set the step size
    # Perform a step
    # Get the positions
    # Issue an altitude command
    # Perform a step
    # Get the positions
    # Get the metrics
    # Perform a step
    # Get the metrics
