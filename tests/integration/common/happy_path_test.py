"""
Basic "happy path" test for any simulator
"""
# NOTE(RKM 2020-01-01) Note that this test isn't run directly, but is imported and
# called by the tests for each simulator
from dataclasses import dataclass
from datetime import datetime

import requests

import tests.integration


@dataclass
class SimUniqueProps:
    sim_type: str
    dt: float
    initial_utc_datetime: datetime


def run_happy_path(props: SimUniqueProps):
    """Runs though a basic scenario covering all the main API functionality"""

    api_base = tests.integration.API_BASE

    resp = requests.post(f"{api_base}/reset")
    assert resp.status_code == 200

    resp = requests.get(f"{api_base}/siminfo")
    assert resp.status_code == 200

    resp_json = resp.json()
    assert resp_json["callsigns"] == []
    assert resp_json["mode"] == "Agent"
    assert resp_json["scenario_name"] == ""
    assert resp_json["scenario_time"] == 0
    assert resp_json["seed"] is None
    assert resp_json["sim_type"].lower() == props.sim_type
    assert resp_json["speed"] == 1  # NOTE This is the DTMULT value in agent mode
    assert resp_json["state"] == "INIT"
    assert resp_json["dt"] == props.dt
    assert resp_json["utc_datetime"] == str(props.initial_utc_datetime)

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
