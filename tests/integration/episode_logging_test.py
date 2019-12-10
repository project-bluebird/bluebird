"""
Tests for episode logging
"""

import re

import pytest
import requests

from tests.integration import API_URL_BASE


def test_episode_logging_agent_mode():
    """
    Tests the the episode log is correctly populated when in agent mode
    """

    pytest.xfail()

    resp = requests.post(f"{API_URL_BASE}/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be set"

    resp = requests.post(f"{API_URL_BASE}/ic", json={"filename": "TEST.scn"})
    assert resp.status_code == 200, "Expected the scenario to be loaded"

    resp = requests.post(f"{API_URL_BASE}/dtmult", json={"multiplier": 10})
    assert resp.status_code == 200, "Expected DTMULT to be set"

    resp = requests.get(f"{API_URL_BASE}/eplog")
    assert resp.status_code == 200, "Expected the episode log to be returned"

    initial_log = resp.json()["lines"]

    # dbg_lines = '\n'.join(initial_log)
    # print(f'initial\n{dbg_lines}')

    assert initial_log, "Expected the log to contain data"

    resp = requests.post(f"{API_URL_BASE}/step")
    assert resp.status_code == 200, "Expected the simulation was stepped"

    resp = requests.get(f"{API_URL_BASE}/eplog")
    assert resp.status_code == 200, "Expected the episode log to be returned"

    updated_log = resp.json()["lines"]

    # dbg_lines = '\n'.join(updated_log)
    # print(f'updated\n{dbg_lines}')

    # Need to account for the case where the initial state gets logged before we pause
    # the sim
    assert (
        len(updated_log) >= len(initial_log) + 2
    ), "Expected at least two more log lines"

    match = re.search(r"C \[(\d)\] STEP", updated_log[-2])
    if not match:
        match = re.search(r"C \[(\d)\] STEP", updated_log[-3])
        assert match is not None, "Expected the step command to be logged"

    init_t = int(match.group(1))

    match = re.search(r"A \[(\d+)\]", updated_log[-1])
    assert match, "Expected aircraft data to have been logged"

    final_t = int(match.group(1))

    assert final_t == init_t + 10, "Expected the log to have been advanced by 10s"
