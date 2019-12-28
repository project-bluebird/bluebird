"""
Tests for the SCENARIO endpoint
"""

import json
from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as original_utils

from tests.unit import API_PREFIX


def test_scenario_post(test_flask_client):
    """Tests the POST method"""

    endpoint = f"{API_PREFIX}/scenario"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "name" in resp.json["message"]

    data = {"name": ""}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "content" in resp.json["message"]

    with mock.patch(
        "bluebird.api.resources.scenario.utils", wraps=original_utils
    ) as utils:

        mock_proxy = mock.MagicMock()
        utils.sim_proxy.return_value = mock_proxy

        # Test no sector set

        mock_proxy.sector = None

        data["content"] = ""
        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode().startswith("A sector definition is required")

        # Test name check

        mock_proxy.sector = True

        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Scenario name must be provided"

        # Test validate_json_scenario

        data["name"] = "TEST"
        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode().startswith("Invalid scenario content")

        # Test error from upload_new_scenario

        mock_proxy.simulation.upload_new_scenario.return_value = (
            "Couldn't upload scenario"
        )

        with open("tests/data/test_scenario.json", "r") as f:
            data = {"name": "test", "content": json.load(f)}

        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode().startswith("Couldn't upload scenario")

        # Test valid response

        mock_proxy.simulation.upload_new_scenario.return_value = None
        resp = test_flask_client.post(endpoint, json=data)
        assert resp.status_code == HTTPStatus.CREATED
