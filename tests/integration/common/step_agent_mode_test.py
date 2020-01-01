"""
Tests for the agent mode and the STEP command
"""

import pytest
import requests

import tests.integration


def test_step_agent_mode():
    """Tests that IC and STEP perform correctly in agent mode with BlueSky"""

    pytest.xfail()

    api_base = tests.integration.API_BASE

    resp = requests.post(f"{api_base}/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be set"

    resp = requests.post(f"{api_base}/ic", json={"filename": "8.SCN"})
    assert resp.status_code == 200, "Expected the scenario to be loaded"

    resp = requests.get(f"{api_base}/pos?acid=SCN1001")
    assert resp.status_code == 200, "Expected to get the aircraft position"

    initial_sim_t = resp.json()["sim_t"]

    resp = requests.post(f"{api_base}/dtmult", json={"multiplier": 20})
    assert resp.status_code == 200, "Expected DTMULT to be set"

    resp = requests.post(f"{api_base}/step")
    assert resp.status_code == 200, "Expected the simulation was stepped"

    resp = requests.get(f"{api_base}/pos?acid=SCN1001")
    assert resp.status_code == 200, "Expected to get the aircraft position"

    diff = resp.json()["sim_t"] - initial_sim_t
    assert 19 <= diff <= 21, "Expected the time diff to be roughly 20 seconds"
