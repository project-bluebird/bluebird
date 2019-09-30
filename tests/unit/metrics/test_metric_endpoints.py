"""
Unit tests for the metric endpoints
"""

# TODO Test vertical/horizontal separation endpoints

# pylint: disable=redefined-outer-name, unused-argument

import pytest

import bluebird.metrics as bb_metrics
import bluebird.settings as bb_settings
from bluebird.cache import AcDataCache, SimState
from tests.unit import API_PREFIX, TEST_ACIDS


@pytest.fixture(scope="module", autouse=True)
def setup_metrics():
    """
    Calls metrics setup once before this module is tested
    :return:
    """

    ac_data = AcDataCache(SimState())
    bb_metrics.setup_metrics(ac_data)


def test_metric_providers(client):
    """
    Tests we can get the available metric providers
    :param client:
    :return:
    """

    resp = client.get(f"{API_PREFIX}/metricproviders")
    assert resp.status == "200 OK"

    expected = {"BlueBirdProvider": str(bb_settings.VERSION)}
    resp_json = resp.get_json()

    assert (
        expected == resp_json
    ), "Expected to see the default BlueBird metrics and version"


def test_metric_endpoint(client, patch_client_sim):
    """
    Tests that invalid inputs are correctly handled
    :return:
    """

    resp = client.get(f"{API_PREFIX}/metric")
    assert resp.status == "400 BAD REQUEST", "Expected no args to return 400"

    resp = client.get(f"{API_PREFIX}/metric?name=test")
    assert resp.status == "404 NOT FOUND", "Expected invalid metric to return 404"

    resp = client.get(f"{API_PREFIX}/metric?name=aircraft_separation")
    assert resp.status == "400 BAD REQUEST", "Expected missing args to return 400"

    resp = client.get(f"{API_PREFIX}/metric?name=aircraft_separation&args=")
    assert resp.status == "400 BAD REQUEST", "Expected no args to return 400"

    resp = client.get(f"{API_PREFIX}/metric?name=aircraft_separation&args=test")
    assert resp.status == "400 BAD REQUEST", "Expected wrong args type to return 400"

    resp = client.get(
        f"{API_PREFIX}/metric?name=aircraft_separation&args={TEST_ACIDS[0]},{TEST_ACIDS[1]}"
    )
    assert resp.status == "200 OK", "Expected valid args to return 200"
