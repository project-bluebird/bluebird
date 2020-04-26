"""
Tests for the LOADLOG endpoint
"""
# NOTE(RKM 2019-11-18) Tests here which rely on the "validate_scenario" utility function
# will fail until we upgrade to the GeoJSON format
import pytest

import bluebird.api.resources.utils.utils as api_utils
from bluebird.api.resources.loadlog import parse_lines
from tests.data import TEST_EPISODE_LOG


API_PREFIX = "FIXME"


def test_parse_lines():
    """Tests the parsing of lines in an episode log"""

    lines = []
    assert isinstance(parse_lines(lines), str), "Expected an error response"

    lines = ["aaaaaa"]
    assert isinstance(parse_lines(lines), str), "Expected an error response"

    lines = [
        "2019-07-11 10:18:28 E Episode started. SIM_LOG_RATE is 0.2 Hz. Seed is None"
    ]
    err = parse_lines(lines)
    assert isinstance(err, str), "Expected an error response"
    assert (
        err == "Episode seed was not set"
    ), "Expected an error regarding the seed not being set"

    lines = [
        "2019-07-11 10:18:28 E Episode started. SIM_LOG_RATE is 0.2 Hz. Seed is 1234"
    ]
    assert isinstance(parse_lines(lines), str), "Expected an error response"

    lines.append("ignored")
    lines.append(
        r"2019-07-11 10:18:29 E Scenario file loaded: scenario\TEST.scn. Contents are:"
    )
    assert isinstance(parse_lines(lines), str), "Expected an error response"

    lines.append("2019-07-11 10:18:29 E 00:00:00.00>CRE Kl204,B744,52,4,90,FL250,350")
    lines.append("2019-07-11 10:18:29 E 00:00:00.50>DEST KL204,EDDF")

    endline = "2019-07-11 10:21:07 E Episode finished (sim reset)"
    lines.append(endline)

    data = parse_lines(lines)
    assert isinstance(data, dict), "Expected some data"
    assert data["seed"] == 1234, "Expected the seed to be set"
    assert len(data["lines"]) == 2, "Expected 2 lines"
    assert data["lines"][0] == "00:00:00.00>CRE Kl204,B744,52,4,90,FL250,350"
    assert data["lines"][1] == "00:00:00.50>DEST KL204,EDDF"

    lines.pop()

    lines.append("2019-07-11 10:18:31 A [2] {data}")
    lines.append("2019-07-11 10:18:31 A [7] {data}")
    assert isinstance(parse_lines(lines), str), "Expected an error response"

    lines.append("2019-07-11 10:19:47 C [78] ALT KL204 9144")
    lines.append("2019-07-11 10:20:08 C [99] ALT KL204 6096")
    assert isinstance(parse_lines(lines), str), "Expected an error response"

    lines.append(endline)
    data = parse_lines(lines)
    assert isinstance(data, dict), "Expected some data"
    assert len(data["lines"]) == 4, "Expected some more commands"
    assert data["lines"][2] == "00:01:18> ALT KL204 9144"
    assert data["lines"][3] == "00:01:39> ALT KL204 6096"


def test_parse_lines_time():
    """Test commands after target time are ignored"""

    lines = [
        "2019-07-11 10:18:28 E Episode started. SIM_LOG_RATE is 0.2 Hz. Seed is 1234",
        "unused",
        "unused",
        "unused",
        r"2019-07-11 10:18:29 E Scenario file loaded: scenario\TEST.scn. Contents are:",
        "2019-07-11 10:18:29 E 00:00:00.00>CRE Kl204,B744,52,4,90,FL250,350",
        "2019-07-11 10:18:29 E 00:00:00.50>DEST KL204,EDDF",
        "2019-07-11 10:19:47 C [78] ALT KL204 9144",
        "2019-07-11 10:20:08 C [100] ALT KL204 6096",
        "2019-07-11 10:21:07 E Episode finished (sim reset)",
    ]

    data = parse_lines(lines, 99)
    assert isinstance(data, dict), "Expected data"
    assert len(data["lines"]) == 3, "Expected 3 commands"
    assert "ALT KL204 9144" in data["lines"][-1], ""


def test_log_reload_from_lines(test_flask_client):
    """Tests the episode reloading given a full logfile in the request"""

    pytest.xfail("Will fail until handling for GeoJSON scenarios is implemented")

    resp = test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be agent"

    resp = test_flask_client.post(API_PREFIX + "/seed", json={"value": 1234})
    assert resp.status_code == 200, "Expected the seed to be set"

    lines = tuple(open(TEST_EPISODE_LOG, "r"))

    data = {"lines": lines, "time": 123}
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 200, "Expected a 200"


def test_log_reload_from_file(test_flask_client):
    """Tests that the episode reloading works when given a logfile"""

    pytest.xfail("Will fail until handling for GeoJSON scenarios is implemented")

    resp = test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be agent"

    resp = test_flask_client.post(API_PREFIX + "/seed", json={"value": 1234})
    assert resp.status_code == 200, "Expected the seed to be set"

    data = {"filename": TEST_EPISODE_LOG.absolute, "time": 123}
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 200, "Expected a 200"


def test_log_reload_full(test_flask_client):
    """Tests the full functionality of the log reloading"""

    pytest.xfail("Will fail until handling for GeoJSON scenarios is implemented")

    resp = test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be agent"

    resp = test_flask_client.post(API_PREFIX + "/seed", json={"value": 1234})
    assert resp.status_code == 200, "Expected the seed to be set"

    data = {"filename": TEST_EPISODE_LOG.absolute, "time": -1}
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 400, "Expected a 400 due to invalid time"

    data["time"] = 120
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 200, "Expected a 200"

    assert (
        api_utils.sim_proxy().simulation.reset_flag
    ), "Expected that the simulator was reset"
    assert (
        api_utils.sim_proxy().simulation.seed == 5678
    ), "Expected that the seed was set"
    assert (
        api_utils.sim_proxy().simulation.scn_uploaded
    ), "Expected that the scenario was uploaded"
    assert (
        api_utils.sim_proxy().simulation.last_scenario
    ), "Expected that the scenario was started"
    assert (
        api_utils.sim_proxy().simulation.was_stepped
    ), "Expected that the simulation was stepped"
    assert (
        api_utils.sim_proxy().simulation.speed_set
    ), "Expected that the simulation had its speed reset"


def test_log_reload_invalid_time(test_flask_client):
    """
    Tests that an error is returned if a reload time was requested which is after the
    last time in the log file
    """

    pytest.xfail("Will fail until handling for GeoJSON scenarios is implemented")

    resp = test_flask_client.post(API_PREFIX + "/seed", json={"value": 1234})
    assert resp.status_code == 200, "Expected the seed to be set"

    lines = tuple(open(TEST_EPISODE_LOG, "r"))

    data = {"lines": lines, "time": 999}
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 400, "Expected a 400"
