"""
Test for https://github.com/alan-turing-institute/nats/issues/70
"""
import pytest
import requests

import tests.integration


def test_issue_core_70():
    """Tests that we can load a scenario which contains the DEFWPT command"""

    pytest.xfail()

    api_base = tests.integration.API_BASE

    resp = requests.post(
        f"{api_base}/ic", json={"filename": "scenario/waypointExp.scn"}
    )
    assert (
        resp.status_code == 500
    ), "Expected the scenario to be loaded, but return a 500"
    assert resp.json().startswith(
        "No aircraft data received"
    ), "Expected the response message to say no data was received"
