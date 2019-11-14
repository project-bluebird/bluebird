"""
Tests for the LOADLOG endpoint
"""

import os
from pathlib import Path

import pytest

from bluebird.api.resources.loadlog import parse_lines
import bluebird.api.resources.utils.utils as utils
from bluebird.utils.properties import SimProperties, SimState

from tests.unit import API_PREFIX

_TEST_FILE = "tests/unit/api/testEpisode.log"
_TEST_FILE_PATH = Path(os.getcwd(), _TEST_FILE)

# pylint: disable=redefined-outer-name, unused-argument, no-member


class MockSimProxy:
    """
    Simple tset mock of the SimProxy class for this test
    """

    # pylint: disable=no-self-use, missing-docstring

    @property
    def sim_properties(self) -> SimProperties:
        return SimProperties(SimState.RUN, 1.0, 1.0, 0.0, "test_scn")

    @property
    def seed(self):
        return self._seed

    def __init__(self):
        self._seed = self.last_scenario = None
        self.reset_flag = self.scn_uploaded = self.was_stepped = False

    def pause_sim(self):
        return None

    def set_seed(self, seed: int):
        assert isinstance(seed, int)
        self._seed = seed

    def reset_sim(self):
        self.reset_flag = True

    def upload_new_scenario(self, scn_name: str, content):
        assert isinstance(scn_name, str)
        assert content
        self.scn_uploaded = True

    def load_scenario(
        self, scenario_name: str, speed: float = 1.0, start_paused: bool = False
    ):
        self.last_scenario = scenario_name

    def set_sim_speed(self, speed: float):
        return None

    def step_sim(self):
        self.was_stepped = True


class MockBlueBird:
    def __init__(self):
        self.sim_proxy = MockSimProxy()


@pytest.fixture
def patch_bb_app_loadlog(monkeypatch):
    """
    Patches the _bb_app function in the api utils module
    """
    mock_bluebird = MockBlueBird()

    def yield_mock():
        return mock_bluebird

    monkeypatch.setattr(utils, "_bb_app", yield_mock)


def test_parse_lines():
    """
    Tests the parsing of lines in an episode log
    :return:
    """

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
    """
    Test commands after target time are ignored
    :return:
    """

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


def test_log_reload_from_lines(test_flask_client, patch_bb_app_loadlog):
    """
    Tests the episode reloading given a full logfile in the request
    :param test_flask_client
    :return:
    """

    resp = test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be agent"

    resp = test_flask_client.post(API_PREFIX + "/seed", json={"value": 1234})
    assert resp.status_code == 200, "Expected the seed to be set"

    assert _TEST_FILE_PATH.exists()
    lines = tuple(open(_TEST_FILE_PATH, "r"))

    data = {"lines": lines, "time": 123}
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 200, "Expected a 200"


def test_log_reload_from_file(test_flask_client, patch_bb_app_loadlog):
    """
    Tests that the episode reloading works when given a logfile
    :param test_flask_client
    :return:
    """

    resp = test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be agent"

    resp = test_flask_client.post(API_PREFIX + "/seed", json={"value": 1234})
    assert resp.status_code == 200, "Expected the seed to be set"

    data = {"filename": _TEST_FILE, "time": 123}
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 200, "Expected a 200"


def test_log_reload_full(test_flask_client, patch_bb_app_loadlog):
    """
    Tests the full functionality of the log reloading
    :param test_flask_client
    :return:
    """

    resp = test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be agent"

    resp = test_flask_client.post(API_PREFIX + "/seed", json={"value": 1234})
    assert resp.status_code == 200, "Expected the seed to be set"

    data = {"filename": _TEST_FILE, "time": -1}
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 400, "Expected a 400 due to invalid time"

    data["time"] = 120
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 200, "Expected a 200"

    assert utils.sim_proxy().reset_flag, "Expected that the simulator was reset"
    assert utils.sim_proxy().seed == 5678, "Expected that the seed was set"
    assert utils.sim_proxy().scn_uploaded, "Expected that the scenario was uploaded"
    assert utils.sim_proxy().last_scenario, "Expected that the scenario was started"
    assert utils.sim_proxy().was_stepped, "Expected that the simulation was stepped"


def test_log_reload_invalid_time(test_flask_client, patch_bb_app_loadlog):
    """
    Tests that an error is returned if a reload time was requested which is after the
    last time in the log file
    :param client:
    :param patch_client_sim:
    :return:
    """

    resp = test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be agent"

    resp = test_flask_client.post(API_PREFIX + "/seed", json={"value": 1234})
    assert resp.status_code == 200, "Expected the seed to be set"

    assert _TEST_FILE_PATH.exists()
    lines = tuple(open(_TEST_FILE_PATH, "r"))

    data = {"lines": lines, "time": 999}
    resp = test_flask_client.post(API_PREFIX + "/loadlog", json=data)
    assert resp.status_code == 400, "Expected a 400"
