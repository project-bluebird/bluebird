"""
Tests for the SECTOR endpoint
"""

import json
from http import HTTPStatus

from aviary.sector.sector_element import SectorElement

from bluebird.sim_proxy.proxy_simulator_controls import Sector

from tests.data import TEST_SECTOR
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import get_app_mock


_ENDPOINT = "sector"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_sector_get(test_flask_client):

    app_mock = get_app_mock(test_flask_client)

    # Test error handling - no sector has been set

    app_mock.sim_proxy.simulation.sector = None

    resp = test_flask_client.get(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # Test error handling - can't get sector as geojson

    app_mock.sim_proxy.simulation.sector = "test"

    resp = test_flask_client.get(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode().startswith("Couldn't get sector geojson")

    # Test OK response - sector has been set

    with open(TEST_SECTOR, "r") as f:
        geojson = json.load(f)
        sector = SectorElement.deserialise(json.dumps(geojson))

    app_mock.sim_proxy.simulation.sector = Sector("test_sector", sector)

    resp = test_flask_client.get(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.OK
    assert resp.json == {"name": "test_sector", "content": geojson}


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
        "Invalid sector content: 'type' is a required property"
    )

    with open(TEST_SECTOR, "r") as f:
        data = {"name": "test", "content": json.load(f)}

    # Test error from load_sector

    app_mock = get_app_mock(test_flask_client)
    app_mock.sim_proxy.simulation.load_sector.return_value = "Error setting sector"

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode() == "Error setting sector"

    # Test CREATED response

    app_mock.sim_proxy.simulation.load_sector.return_value = None

    resp = test_flask_client.post(_ENDPOINT_PATH, json=data)
    assert resp.status_code == HTTPStatus.CREATED
