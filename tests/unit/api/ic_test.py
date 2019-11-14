"""
Tests for the IC endpoint
"""

from http import HTTPStatus

from tests.unit import API_PREFIX

import bluebird.api.resources.utils.utils as utils
import bluebird.settings as bb_settings
from bluebird.utils.properties import SimMode

_ENDPOINT = f"{API_PREFIX}/ic"


def test_ic_get(test_flask_client, patch_sim_proxy):  # pylint: disable=unused-argument
    """
    Tests the GET method
    """

    # Test error handling

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR

    # Test valid response

    resp = test_flask_client.get(_ENDPOINT)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"scn_name": "test_scn"}


def test_ic_post(test_flask_client, patch_sim_proxy):  # pylint: disable=unused-argument
    """
    Tests the POST method
    """

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    data = {"filename": "", "multiplier": -1.0}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "No filename specified"

    # Test multiplier check

    test_scenario = "new_scenario.json"
    data["filename"] = test_scenario
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == f"Invalid speed {data['multiplier']}"

    # Test load_scenario - Sandbox mode

    data["multiplier"] = 1.5
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.OK

    load_scn_args = utils.sim_proxy().last_scn
    expected_args = {
        "scenario_name": test_scenario,
        "speed": 1.5,
        "start_paused": False,
    }
    assert load_scn_args == expected_args

    # Test load_scenario - Agent mode

    bb_settings.Settings.SIM_MODE = SimMode.Agent
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.OK

    load_scn_args = utils.sim_proxy().last_scn
    expected_args["start_paused"] = True
    assert load_scn_args == expected_args
