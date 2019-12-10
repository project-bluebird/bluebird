"""
Test for https://github.com/alan-turing-institute/nats/issues/70
"""

import pytest
import requests

from tests.integration import API_URL_BASE


def test_issue_core_70():
    """
    Tests that we can load a scenario which contains the DEFWPT command
    :return:
    """

    pytest.xfail()

    resp = requests.post(
        f"{API_URL_BASE}/ic", json={"filename": "scenario/waypointExp.scn"}
    )
    assert (
        resp.status_code == 500
    ), "Expected the scenario to be loaded, but return a 500"
    assert resp.json().startswith(
        "No aircraft data received"
    ), "Expected the response message to say no data was received"
