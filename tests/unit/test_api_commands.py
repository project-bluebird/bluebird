"""
Tests each of the API endpoints.

Provides a Flask test_client fixture which is generated from the BlueBird app definition. This
is then used to test the app endpoints with various HTTP requests. Test aircraft data is manually
defined, so we don't have any test dependencies on BlueSky.
"""

# pylint: disable=redefined-outer-name, unused-argument, no-member

import os

import bluebird.settings as settings
from bluebird.api.resources.utils import bb_app
from tests.unit import API_PREFIX, SIM_DATA, TEST_ACIDS, TEST_DATA, TEST_DATA_KEYS


def test_pos_command(test_flask_client):
    """
	Tests the /pos endpoint
	:param test_flask_client:
	:return:
	"""

    resp = test_flask_client.get(API_PREFIX + "/pos")
    assert resp.status == "400 BAD REQUEST"

    resp = test_flask_client.get(API_PREFIX + "/pos", json={"acid": "TST1001"})
    assert resp.status == "400 BAD REQUEST"

    resp = test_flask_client.get(API_PREFIX + "/pos?acid=unknown")
    assert resp.status == "404 NOT FOUND"

    for idx in range(len(TEST_DATA["id"])):
        acid = TEST_DATA["id"][idx]

        resp = test_flask_client.get(API_PREFIX + "/pos?acid={}".format(acid))
        assert resp.status == "200 OK"

        resp_json = resp.get_json()

        assert len(resp_json) == 2
        assert SIM_DATA[2] == resp_json["sim_t"]

        ac_data = resp_json[acid]

        assert len(ac_data) == len(TEST_DATA) - 1  # 'id' not included in response
        assert set(ac_data.keys()) == set(TEST_DATA_KEYS)

        for prop in ac_data:
            assert TEST_DATA[prop][idx] == ac_data[prop]


def test_ic_command(test_flask_client):
    """
	Tests the /ic endpoint
	:param test_flask_client:
	:return:
	"""

    resp = test_flask_client.post(API_PREFIX + "/ic")
    assert resp.status == "400 BAD REQUEST"

    resp = test_flask_client.post(API_PREFIX + "/ic", json={})
    assert resp.status == "400 BAD REQUEST"

    filename = "testeroni.scn"

    resp = test_flask_client.post(API_PREFIX + "/ic", json={"filename": filename})
    assert resp.status == "200 OK"

    assert (
        bb_app().sim_client.last_scenario == filename
    ), "Expected the filename to be loaded"

    filename = "testeroni.SCN"

    resp = test_flask_client.post(API_PREFIX + "/ic", json={"filename": filename})
    assert resp.status == "200 OK"

    assert (
        bb_app().sim_client.last_scenario == filename
    ), "Expected the filename to be loaded"


def test_reset_command(test_flask_client):
    """
	Tests the /reset endpoint
	:param test_flask_client:
	:return:
	"""

    resp = test_flask_client.post(API_PREFIX + "/reset")
    assert resp.status == "200 OK"

    assert bb_app().sim_client.was_reset, "Expected the client simulation to be reset"


def test_cre_new_aircraft(test_flask_client):
    """
	Test the CRE endpoint handles new aircraft correctly
	:param test_flask_client
	:return:
	"""

    acid = "TST1234"
    assert not bb_app().ac_data.contains(
        acid
    ), "Expected the test aircraft not to exist"

    cre_data = {
        "acid": acid,
        "type": "testeroni",
        "lat": 0,
        "lon": 0,
        "hdg": 0,
        "alt": 0,
        "spd": 0,
    }
    resp = test_flask_client.post(API_PREFIX + "/cre", json=cre_data)

    assert resp.status == "201 CREATED"


def test_cre_existing_aircraft(test_flask_client):
    """
	Test the CRE endpoint handles existing aircraft correctly
	:param test_flask_client
	:return:
	"""

    acid = TEST_ACIDS[0]
    assert bb_app().ac_data.get(acid) is not None, "Expected the test aircraft to exist"

    cre_data = {
        "acid": acid,
        "type": "testeroni",
        "lat": 0,
        "lon": 0,
        "hdg": 0,
        "alt": 0,
        "spd": 0,
    }
    resp = test_flask_client.post(API_PREFIX + "/cre", json=cre_data)

    assert resp.status == "400 BAD REQUEST"


def test_scenario_endpoint(test_flask_client):
    """
	Tests the create scenario endpoint
	:param test_flask_client
	:return:
	"""

    resp = test_flask_client.post(API_PREFIX + "/scenario")
    assert resp.status == "400 BAD REQUEST"

    data = {"scn_name": "new-scenario", "content": []}

    resp = test_flask_client.post(API_PREFIX + "/scenario", json=data)
    assert resp.status == "400 BAD REQUEST"

    data["content"] = ["invalid", "invalid"]

    resp = test_flask_client.post(API_PREFIX + "/scenario", json=data)
    assert resp.status == "400 BAD REQUEST"

    data["content"] = [
        "00:00:00>CRE TEST A320 0 0 0 0",
        "00:00:00 > CRE TEST A320 0 0 0 0",
    ]

    resp = test_flask_client.post(API_PREFIX + "/scenario", json=data)
    assert resp.status == "201 CREATED"

    data["start_new"] = True
    data["start_dtmult"] = 1.23

    resp = test_flask_client.post(API_PREFIX + "/scenario", json=data)
    assert resp.status == "200 OK"

    assert (
        bb_app().sim_client.last_scenario == "new-scenario.scn"
    ), "Expected the filename to be loaded"
    assert bb_app().sim_client.last_dtmult == 1.23, "Expected the dtmult to be set"

    # Remove the test file from the BlueSky submodule
    try:
        os.remove("bluesky/scenario/new-scenario.scn")
    except OSError:
        pass


def test_change_mode(test_flask_client):
    """
	Tests the functionality of the simmode endpoint
	:param test_flask_client
	:return:
	"""

    assert settings.SIM_MODE == "sandbox", "Expected the initial mode to be sandbox"

    data = {"mode": "test"}
    resp = test_flask_client.post(API_PREFIX + "/simmode", json=data)

    assert resp.status == "400 BAD REQUEST", "Expected an invalid mode to return 400"

    data["mode"] = "agent"
    resp = test_flask_client.post(API_PREFIX + "/simmode", json=data)

    assert resp.status == "200 OK", "Expected a valid mode to return 200"
    assert settings.SIM_MODE == "agent", "Expected the final mode to be agent"


def test_non_agent_mode_step(test_flask_client):
    """
	Tests that the sim is not stepped if in the sandbox mode
	:param test_flask_client
	:return:
	"""

    test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "sandbox"})
    assert settings.SIM_MODE == "sandbox", "Expected the initial mode to be sandbox"

    resp = test_flask_client.post(f"{API_PREFIX}/step")
    assert resp.status_code == 400, "Expected a 400 BAD REQUEST"
    assert (
        not bb_app().sim_client.was_stepped
    ), "Expected the simulation was not stepped forward"


def test_agent_mode_step(test_flask_client):
    """
	Tests that the sim is stepped if in agent mode
	:param test_flask_client
	:return:
	"""

    test_flask_client.post(API_PREFIX + "/simmode", json={"mode": "agent"})
    assert settings.SIM_MODE == "agent", "Expected the mode to be agent"

    resp = test_flask_client.post(f"{API_PREFIX}/step")
    assert resp.status_code == 200, "Expected a 200 response"
    assert (
        bb_app().sim_client.was_stepped
    ), "Expected the simulation was stepped forward"


def test_set_seed(test_flask_client):
    """
	Tests the functionality of the seed endpoint
	:param test_flask_client
	:return:
	"""

    resp = test_flask_client.post(API_PREFIX + "/seed")
    assert resp.status == "400 BAD REQUEST"

    data = {"test": 1234}

    resp = test_flask_client.post(API_PREFIX + "/seed", json=data)
    assert resp.status == "400 BAD REQUEST"

    data = {"value": "test"}

    resp = test_flask_client.post(API_PREFIX + "/seed", json=data)
    assert resp.status == "400 BAD REQUEST"

    data = {"value": -123}

    resp = test_flask_client.post(API_PREFIX + "/seed", json=data)
    assert resp.status == "400 BAD REQUEST"

    data = {"value": 123}

    resp = test_flask_client.post(API_PREFIX + "/seed", json=data)
    assert resp.status == "200 OK"
    assert bb_app().sim_client.seed == 123, ""

    data = {"value": 2 ** 32 - 1}
    resp = test_flask_client.post(API_PREFIX + "/seed", json=data)
    assert resp.status == "200 OK"

    data = {"value": 2 ** 32}
    resp = test_flask_client.post(API_PREFIX + "/seed", json=data)
    assert resp.status == "400 BAD REQUEST"


def test_alt_fl_parsing(test_flask_client):
    """
	Tests that we correctly parse the altitude argument
	:param test_flask_client
	:return:
	"""

    acid = TEST_ACIDS[0]
    data = {"acid": acid, "alt": "FL120"}

    resp = test_flask_client.post(API_PREFIX + "/alt", json=data)
    assert resp.status_code == 200, "Expected OK"
    assert (
        bb_app().sim_client.last_stack_cmd == "ALT TST1001 FL120"
    ), "Expected ALT to match"

    data["alt"] = "12345"

    resp = test_flask_client.post(API_PREFIX + "/alt", json=data)
    assert resp.status_code == 200, "Expected OK"
    assert (
        bb_app().sim_client.last_stack_cmd == "ALT TST1001 12345"
    ), "Expected ALT to match"
