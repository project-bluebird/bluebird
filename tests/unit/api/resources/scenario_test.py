"""
Tests for the SCENARIO endpoint
"""

import json
from http import HTTPStatus

import mock

import bluebird.api.resources.utils.utils as utils
from bluebird.sim_proxy.sim_proxy import SimProxy
from bluebird.sim_proxy.proxy_simulator_controls import ProxySimulatorControls

from tests.data import TEST_SCENARIO
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "scenario"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


@mock.patch(patch_utils_path(_ENDPOINT), wraps=utils, spec_set=True)
def test_scenario_post(utils_patch, test_flask_client):
    """Tests the POST method"""

    sim_proxy_mock = mock.create_autospec(SimProxy, spec_set=True)
    utils_patch.sim_proxy.return_value = sim_proxy_mock
    simulation_mock = mock.create_autospec(ProxySimulatorControls, spec_set=True)
    type(sim_proxy_mock).simulation = mock.PropertyMock(return_value=simulation_mock)
    sector_mock = mock.PropertyMock(return_value=None)
    type(simulation_mock).sector = sector_mock

    # Test arg parsing

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "name" in resp.json["message"]

    # Test no sector set

    data = {"name": ""}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith("A sector definition is required")

    # Test name check

    sector_mock.return_value = True

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Scenario name must be provided"

    # Test validate_json_scenario

    data = {"name": "test-scenario", "content": {"wrong": "format"}}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith("Invalid scenario content")

    # Test error from load_scenario

    simulation_mock.load_scenario.return_value = "Couldn't load scenario"

    with open(TEST_SCENARIO, "r") as f:
        data["content"] = json.load(f)

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode().startswith("Couldn't load scenario")

    # Test valid response - new scenario provided

    simulation_mock.load_scenario.return_value = None

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.CREATED

    # Test valid response - load existing scenario by name

    data["content"] = {}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.CREATED
