"""
Tests for the SECTOR endpoint
"""

import json
from http import HTTPStatus

import mock
import pytest
from aviary.sector.sector_element import SectorElement

import bluebird.api.resources.utils.utils as utils
from bluebird.sim_proxy.proxy_simulator_controls import Sector

from tests.data import TEST_SECTOR
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "sector"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_sector_get(test_flask_client):

    with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error handling - no sector has been set

        sim_proxy_mock.sector = None

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

        # Test error handling - can't get sector as geojson

        sim_proxy_mock.sector = "test"

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode().startswith("Couldn't get sector geojson")

        # Test OK response - sector has been set

        with open(TEST_SECTOR, "r") as f:
            geojson = json.load(f)
            del geojson["_source"]
            sector = SectorElement.deserialise(json.dumps(geojson))

        sim_proxy_mock.sector = Sector("test_sector", sector)

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.OK

        # NOTE(RKM 2019-12-29) Broken for now until SectorElement.deserialise is fixed
        # assert resp.json == {"name": "test_sector", "content": geojson}
        pytest.xfail()


def test_sector_post(test_flask_client):

    # Test error handling - invalid args

    resp = test_flask_client.post(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.post(_ENDPOINT_PATH, json={})
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.post(_ENDPOINT_PATH, json={"content": {}})
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.post(_ENDPOINT_PATH, json={"name": "", "content": {}})
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Sector name must be provided"

    # Test error handling - content did not pass validation check

    # Missing type
    data = {"name": "test", "content": {"features": []}}
    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith(
        "Invalid scenario content: 'type' is a required property"
    )

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        with open(TEST_SECTOR, "r") as f:
            data = {"name": "test", "content": json.load(f)}

        # Test error from set_sector

        sim_proxy_mock.simulation.set_sector.return_value = "Error setting sector"

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Error setting sector"

        # Test CREATED response

        sim_proxy_mock.simulation.set_sector.return_value = None

        resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
        assert resp.status_code == HTTPStatus.CREATED
