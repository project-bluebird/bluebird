"""
Tests for the episode reloading
"""
import pytest
import requests
from pyproj import Geod

import tests.integration


_WGS84 = Geod(ellps="WGS84")
_ONE_NM = 1852  # Meters
_ONE_FT = 0.3048  # Meters


def test_episode_reload_basic():
    """
    Tests the basic functionality of the episode reloading
    :return:
    """

    pytest.xfail()

    api_base = tests.integration.API_BASE

    test_acid = "KL204"

    resp = requests.post(f"{api_base}/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be set"

    resp = requests.post(f"{api_base}/seed", json={"value": 123123})
    assert resp.status_code == 200, "Expected that the seed was set"

    resp = requests.post(f"{api_base}/ic", json={"filename": "TEST.scn"})
    assert resp.status_code == 200, "Expected that the scenario was loaded"

    resp = requests.post(f"{api_base}/dtmult", json={"multiplier": 20})
    assert resp.status_code == 200, "Expected DTMULT to be set"

    # Do an initial step
    resp = requests.post(f"{api_base}/step")
    assert resp.status_code == 200, "Expected the simulation was stepped"

    # Change altitude and heading
    resp = requests.post(f"{api_base}/alt", json={"acid": test_acid, "alt": "FL100"})
    assert resp.status_code == 200, "Expected the aircraft altitude to be changed"

    resp = requests.post(f"{api_base}/hdg", json={"acid": test_acid, "hdg": "180"})
    assert resp.status_code == 200, "Expected the aircraft heading to be changed"

    for _ in range(3):
        resp = requests.post(f"{api_base}/step")
        assert resp.status_code == 200, "Expected the simulation was stepped"

    # Get the position here
    resp = requests.get(f"{api_base}/pos?acid={test_acid}")
    assert resp.status_code == 200, "Expected to get the aircraft position"

    initial_t = resp.json()["sim_t"]
    initial_pos = resp.json()[test_acid]

    # Step some more
    for _ in range(3):
        resp = requests.post(f"{api_base}/step")
        assert resp.status_code == 200, "Expected the simulation was stepped"

    # Now get the episode log and reload to the middle of the log

    resp = requests.get(f"{api_base}/eplog")
    assert resp.status_code == 200, "Expected to receive the episode log"

    episode_file = resp.json()["cur_ep_file"]
    data = {"filename": episode_file, "time": initial_t}
    resp = requests.post(f"{api_base}/loadlog", json=data)
    assert resp.status_code == 200, "Expected the simulation was reloaded"

    # Now get the reloaded position and compare with the initial

    resp = requests.get(f"{api_base}/pos?acid={test_acid}")
    assert resp.status_code == 200, "Expected to get the aircraft position"

    reloaded_t = resp.json()["sim_t"]
    reloaded_pos = resp.json()[test_acid]

    assert (
        abs(reloaded_t - initial_t) <= 1
    ), "Expected the reloaded time to be at the target"

    _, _, horizontal_sep_m = _WGS84.inv(
        initial_pos["lon"], initial_pos["lat"], reloaded_pos["lon"], reloaded_pos["lat"]
    )

    # TODO Check the deltas are reasonable...
    assert round(horizontal_sep_m / _ONE_NM) <= 5, "Expected positions to roughly match"
    assert (
        abs(reloaded_pos["alt"] - initial_pos["alt"]) <= 100 / _ONE_FT
    ), "Expected altitudes to roughly match"
    assert (
        abs(reloaded_pos["gs"] - initial_pos["gs"]) <= 50
    ), "Expected ground speeds to roughly match"
    assert (
        abs(reloaded_pos["vs"] - initial_pos["vs"]) <= 50
    ), "Expected vertical speeds to roughly match"
