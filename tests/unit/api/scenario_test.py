"""
Tests for the SCENARIO endpoint
"""

from http import HTTPStatus

import pytest

import bluebird.api.resources.utils.utils as api_utils

from tests.unit import API_PREFIX
from tests.unit.api import MockBlueBird


class MockSimulatorControls:
    # TODO(RKM 2019-11-18) Will need - supload_new_scenario, load_scenario
    pass


@pytest.fixture
def _set_bb_app(monkeypatch):
    mock = MockBlueBird()
    mock.sim_proxy.set_props(None, MockSimulatorControls(), None)
    monkeypatch.setattr(api_utils, "_bb_app", lambda: mock)


def test_scenario_post(
    test_flask_client, _set_bb_app
):  # pylint: disable=unused-argument
    """
    Tests the POST method
    """

    endpoint = f"{API_PREFIX}/scenario"

    # Test arg parsing

    resp = test_flask_client.post(endpoint)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "scn_name" in resp.json["message"]

    data = {"scn_name": ""}
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert "content" in resp.json["message"]

    # Test scn_name check

    data["content"] = [""]
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.data.decode() == "Scenario name must be provided"

    data["scn_name"] = "TEST"
    resp = test_flask_client.post(endpoint, json=data)
    assert resp.status_code == HTTPStatus.BAD_REQUEST

    # TODO: Update this once the GeoJSON upload is implemented
    assert (
        resp.data.decode()
        == "Invalid scenario content: validate_scenario is depreciated"
    )


# def test_scenario_endpoint(test_flask_client):
#     """
#     Tests the create scenario endpoint
#     :param test_flask_client
#     :return:
#     """

#     resp = test_flask_client.post(API_PREFIX + "/scenario")
#     assert resp.status == "400 BAD REQUEST"

#     data = {"scn_name": "new-scenario", "content": []}

#     resp = test_flask_client.post(API_PREFIX + "/scenario", json=data)
#     assert resp.status == "400 BAD REQUEST"

#     data["content"] = ["invalid", "invalid"]

#     resp = test_flask_client.post(API_PREFIX + "/scenario", json=data)
#     assert resp.status == "400 BAD REQUEST"

#     data["content"] = [
#         "00:00:00>CRE TEST A320 0 0 0 0",
#         "00:00:00 > CRE TEST A320 0 0 0 0",
#     ]

#     resp = test_flask_client.post(API_PREFIX + "/scenario", json=data)
#     assert resp.status == "201 CREATED"

#     data["start_new"] = True
#     data["start_dtmult"] = 1.23

#     resp = test_flask_client.post(API_PREFIX + "/scenario", json=data)
#     assert resp.status == "200 OK"

#     assert (
#         bb_app().sim_client.last_scenario == "new-scenario.scn"
#     ), "Expected the filename to be loaded"
#     assert bb_app().sim_client.last_dtmult == 1.23, "Expected the dtmult to be set"

#     # Remove the test file from the BlueSky submodule
#     try:
#         os.remove("bluesky/scenario/new-scenario.scn")
#     except OSError:
#         pass
