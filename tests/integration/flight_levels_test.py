"""
Tests for the flight level commands
"""


import requests

from tests.integration import API_URL_BASE


def test_get_flight_levels():
    """
    Tests that the correct flight levels are returned
    :return:
    """

    resp = requests.post(f"{API_URL_BASE}/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be set"

    scn_data = {
        "scn_name": "test_get_flight_levels",
        "content": [
            "00:00:00> CRE AC0006 B744 0 0 0 FL250 250",
            "00:00:00.1> ADDWPT AC0006,-1.84189483394,-0.118823382978,9500.0,351.123056728",  # noqa: E501
            "00:00:00.1> ADDWPT AC0006,-2.97563956062,-2.23988660389,,351.123056728",
            "00:00:00.1> ADDWPT AC0006,-3.22494198491,-2.70468585088,0.0,400.0",
            "00:00:00.1> LNAV AC0006 ON",
            "00:00:00.1> VNAV AC0006 ON",
        ],
        "start_new": True,
    }

    resp = requests.post(f"{API_URL_BASE}/scenario", json=scn_data)
    assert resp.status_code == 200, "Expected the scenario to be uploaded"

    test_acid = "AC0006"

    resp = requests.get(f"{API_URL_BASE}/pos?acid={test_acid}")
    assert resp.status_code == 200, "Expected to get the aircraft position"
    assert (
        resp.json()[test_acid]["alt"] == 7620
    ), "Expected the initial flight level to be FL250"

    resp = requests.get(f"{API_URL_BASE}/listroute?acid=AC0006")
    assert resp.status_code == 200, "Expected to get the aircraft route"

    fl_requested = None
    for part in resp.json()["route"]:
        if part["is_current"]:
            fl_requested = part["req_alt"]

    assert fl_requested == "FL95", "Expected the requested flight level to be set"

    resp = requests.post(
        f"{API_URL_BASE}/alt", json={"acid": test_acid, "alt": "FL150"}
    )
    assert resp.status_code == 200, "Expected to set the cleared altitude"

    # Check we get the correct flight levels back

    resp = requests.get(f"{API_URL_BASE}/alt?acid={test_acid}")
    assert resp.status_code == 200, "Expected to get the flight levels"

    assert (
        resp.json()["fl_current"] == 7620
    ), "Expected the current flight level to be correct"
    assert (
        resp.json()["fl_cleared"] == 4572
    ), "Expected the cleared flight level to be correct"
    assert (
        resp.json()["fl_requested"] == 2896
    ), "Expected the requested flight level to be correct"


def test_initial_cleared_flight_level():
    """
    Tests that the initial cleared flight level is set correctly
    :return:
    """

    resp = requests.post(f"{API_URL_BASE}/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be set"

    scn_data = {
        "scn_name": "test_cleared_flight_level",
        "content": [
            "00:00:00> CRE AC0006 B744 0 0 0 FL250 250",
            "00:00:00.1> ADDWPT AC0006,-1.84189483394,-0.118823382978,9500.0,351.123056728",  # noqa: E501
            "00:00:00.1> ADDWPT AC0006,-2.97563956062,-2.23988660389,,351.123056728",
            "00:00:00.1> ADDWPT AC0006,-3.22494198491,-2.70468585088,0.0,400.0",
            "00:00:00.1> LNAV AC0006 ON",
            "00:00:00.1> VNAV AC0006 ON",
        ],
        "start_new": True,
    }

    resp = requests.post(f"{API_URL_BASE}/scenario", json=scn_data)
    assert resp.status_code == 200, "Expected the scenario to be uploaded"

    test_acid = "AC0006"

    resp = requests.get(f"{API_URL_BASE}/pos?acid={test_acid}")
    assert resp.status_code == 200, "Expected to get the aircraft position"
    assert (
        resp.json()[test_acid]["alt"] == 7620
    ), "Expected the initial flight level to be FL250"

    resp = requests.get(f"{API_URL_BASE}/alt?acid={test_acid}")
    assert resp.status_code == 200, "Expected "
    assert (
        resp.json()["fl_cleared"] == 7620
    ), "Expected the cleared flight level to be the same as the initial"
