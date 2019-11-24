"""
Basic "happy path" test for any simulator
"""

import requests

from tests.integration import API_URL_BASE


def happy_path():

    resp = requests.post(f"{API_URL_BASE}/reset")
    assert resp.status_code == 200

    # TODO(RKM 2019-11-23) Replace with GeoJSON scenario upload
    # Load a scenario
    data = {"filename": "8.SCN"}
    resp = requests.post(f"{API_URL_BASE}/ic", json=data)
    assert resp.status_code == 200

    # Get the status
    resp = requests.get(f"{API_URL_BASE}/siminfo")
    assert resp.status_code == 200
    assert resp.json() == {
        "callsigns": ["SCN1003", "SCN1005", "SCN1002", "SCN1001", "SCN1004", "SCN1008"],
        "mode": "Agent",
        "scenario_name": "8",
        "scenario_time": 0.55,
        "seed": 0,
        "sim_type": "BlueSky",
        "speed": 0.65,
        "state": "HOLD",
        "step_size": 1,
        "utc_time": "2019-11-24 0",
    }

    # Set the step size
    # Perform a step
    # Get the positions
    # Issue an altitude command
    # Perform a step
    # Get the positions
    # Get the metrics
    # Perform a step
    # Get the metrics
