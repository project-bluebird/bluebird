"""
Tests for the SCENARIO endpoint
"""

import json
from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as utils

from tests.data import TEST_SCENARIO
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "scenario"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_scenario_post(test_flask_client):
    """Tests the POST method"""

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "name" in resp.json["message"]

    data = {"name": ""}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "content" in resp.json["message"]

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test no sector set

        sim_proxy_mock.simulation.sector = None

        data["content"] = ""
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode().startswith("A sector definition is required")

        # Test name check

        sim_proxy_mock.simulation.sector = True

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Scenario name must be provided"

        # Test validate_json_scenario

        data["name"] = "TEST"
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode().startswith("Invalid scenario content")

        # Test error from upload_new_scenario

        sim_proxy_mock.simulation.upload_new_scenario.return_value = (
            "Couldn't upload scenario"
        )

        with open(TEST_SCENARIO, "r") as f:
            data = {"name": "test", "content": json.load(f)}

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode().startswith("Couldn't upload scenario")

        # Test valid response

        sim_proxy_mock.simulation.upload_new_scenario.return_value = None
        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.CREATED
