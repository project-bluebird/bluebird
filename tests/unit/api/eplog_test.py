"""
Tests for the EPLOG endpoint
"""

import os
from pathlib import Path
from http import HTTPStatus

import bluebird.logging as bb_logging

from tests.unit import API_PREFIX


def test_eplog_get(test_flask_client, patch_bb_app):  # pylint: disable=unused-argument
    """
    Tests the GET method
    """

    endpoint = f"{API_PREFIX}/eplog"

    # Test arg parsing

    bb_logging.EP_FILE = None
    resp = test_flask_client.get(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "No episode being recorded"

    resp = test_flask_client.get(f"{endpoint}?close_ep=True")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "No episode being recorded"

    # Test close_ep

    bb_logging.EP_FILE = "fake.log"
    resp = test_flask_client.get(f"{endpoint}?close_ep=True")
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode().startswith("Could not reset simulation")

    # Test missing file

    resp = test_flask_client.get(f"{endpoint}?close_ep=True")
    assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
    assert resp.data.decode().startswith("Could not find episode file")

    test_eplog_path = "tests/unit/api/testEpisode.log"
    bb_logging.EP_FILE = test_eplog_path
    bb_logging.EP_ID = 123
    resp = test_flask_client.get(f"{endpoint}?close_ep=True")
    assert resp.status_code == HTTPStatus.OK

    test_eplog_file = Path(os.getcwd(), test_eplog_path)
    assert resp.json == {
        "cur_ep_id": 123,
        "cur_ep_file": str(test_eplog_file),
        "lines": list(line.rstrip("\n") for line in open(test_eplog_file)),
    }
