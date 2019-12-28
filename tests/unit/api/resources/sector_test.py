"""
Tests for the SECTOR endpoint
"""

import json
from http import HTTPStatus

import mock
from aviary.sector.sector_element import SectorElement

import bluebird.api.resources.utils.utils as original_utils
from bluebird.sim_proxy.sim_proxy import Sector

from tests.unit import API_PREFIX


_ENDPOINT = f"{API_PREFIX}/sector"


def test_sector_get(test_flask_client):

    with mock.patch("bluebird.api.resources.sector.utils") as utils:

        mock_proxy = mock.MagicMock()
        utils.sim_proxy.return_value = mock_proxy

        # Test error handling - no sector has been set

        mock_proxy.sector = None

        resp = test_flask_client.get(_ENDPOINT)
        assert resp.status_code == HTTPStatus.BAD_REQUEST

        # Test error handling - can't get sector as geojson

        mock_proxy.sector = "test"

        resp = test_flask_client.get(_ENDPOINT)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode().startswith("Couldn't get sector geojson")

        # Test OK response - sector has been set

        with open("tests/data/test_sector.geojson", "r") as f:
            geojson = json.load(f)
            del geojson["_source"]
            sector = SectorElement.deserialise(json.dumps(geojson))

        mock_proxy.sector = Sector("test_sector", sector)

        resp = test_flask_client.get(_ENDPOINT)
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {"name": "test_sector", "content": geojson}


def test_sector_post(test_flask_client):

    # Test error handling - invalid args

    resp = test_flask_client.post(_ENDPOINT)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.post(_ENDPOINT, json={})
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.post(_ENDPOINT, json={"content": {}})
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    resp = test_flask_client.post(_ENDPOINT, json={"name": "", "content": {}})
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Sector name must be provided"

    # Test error handling - content did not pass validation check

    # Missing type
    data = {"name": "test", "content": {"features": []}}
    resp = test_flask_client.post(_ENDPOINT, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode().startswith(
        "Invalid scenario content: 'type' is a required property"
    )

    with mock.patch(
        "bluebird.api.resources.sector.utils", wraps=original_utils
    ) as utils:

        mock_proxy = mock.MagicMock()
        utils.sim_proxy.return_value = mock_proxy

        with open("tests/data/test_sector.geojson", "r") as f:
            data = {"name": "test", "content": json.load(f)}

        # Test error from set_sector

        mock_proxy.set_sector.return_value = "Error setting sector"

        resp = test_flask_client.post(_ENDPOINT, json=data)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Error setting sector"

        # Test CREATED response

        mock_proxy.set_sector.return_value = None

        resp = test_flask_client.post(_ENDPOINT, json=data)
        assert resp.status_code == HTTPStatus.CREATED
