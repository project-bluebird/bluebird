"""
Tests for the IC endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as utils

from tests.unit.api.resources import endpoint_path, patch_utils_path, TEST_SIM_PROPS


_ENDPOINT = "ic"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_ic_get(test_flask_client):
    """Tests the GET method"""

    with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

        sim_proxy_mock = mock.MagicMock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from simulation properties

        sim_proxy_mock.simulation.properties = "Error"

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't get sim properties: Error"

        # Test valid response

        sim_proxy_mock.simulation.properties = TEST_SIM_PROPS

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {"scenario_name": TEST_SIM_PROPS.scenario_name}


def test_ic_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test filename check

    data = {"filename": "", "multiplier": -1.0}

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "No filename specified"

    # Test multiplier check

    test_scenario = "new_scenario.json"
    data["filename"] = test_scenario

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == f"Invalid speed {data['multiplier']}"

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        sim_proxy_mock = mock.MagicMock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error handling

        sim_proxy_mock.simulation.load_scenario.return_value = "Couldn't load scenario"

        data["multiplier"] = 1.5

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't load scenario"

        # Test valid response

        sim_proxy_mock.simulation.load_scenario.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.OK
