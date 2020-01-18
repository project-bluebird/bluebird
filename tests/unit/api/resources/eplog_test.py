"""
Tests for the EPLOG endpoint
"""
from http import HTTPStatus
from pathlib import Path

import mock

import bluebird.logging as bb_logging
from tests.data import TEST_EPISODE_LOG
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path


_ENDPOINT = "eplog"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_eplog_get(test_flask_client):
    """Tests the GET method"""

    # Test arg parsing

    bb_logging.EP_FILE = None
    resp = test_flask_client.get(_ENDPOINT_PATH)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "No episode being recorded"

    with mock.patch(
        "bluebird.api.resources.eplog.in_agent_mode"
    ) as in_agent_mode_patch:

        in_agent_mode_patch.return_value = False

        # Test agent mode check

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Episode data only recorded when in Agent mode"

        # Test episode file check

        in_agent_mode_patch.return_value = True

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "No episode being recorded"

        with mock.patch("bluebird.api.resources.eplog.bb_logging") as bb_logging_patch:

            bb_logging_patch.EP_FILE = Path("missing.log")

            with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

                sim_proxy_mock = mock.Mock()
                utils_patch.sim_proxy.return_value = sim_proxy_mock

                # Test error from simulation reset

                sim_proxy_mock.simulation.reset.return_value = "Error"

                resp = test_flask_client.get(f"{_ENDPOINT_PATH}?close_ep=True")
                assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
                assert resp.data.decode().startswith("Couldn't reset simulation: Error")

                # Test missing file

                sim_proxy_mock.simulation.reset.return_value = None

                resp = test_flask_client.get(f"{_ENDPOINT_PATH}?close_ep=True")
                assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
                assert resp.data.decode().startswith("Could not find episode file")

                # Test valid response

                bb_logging_patch.EP_FILE = TEST_EPISODE_LOG
                bb_logging_patch.EP_ID = 123

                resp = test_flask_client.get(f"{_ENDPOINT_PATH}?close_ep=True")
                assert resp.status_code == HTTPStatus.OK
                assert resp.json == {
                    "cur_ep_id": 123,
                    "cur_ep_file": str(TEST_EPISODE_LOG.absolute()),
                    "log": list(line.rstrip("\n") for line in open(TEST_EPISODE_LOG)),
                }
