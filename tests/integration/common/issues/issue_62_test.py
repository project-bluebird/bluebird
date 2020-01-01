"""
Test for https://github.com/alan-turing-institute/bluebird/issues/62
"""

import pytest
import requests

import tests.integration


def test_issue_62():
    """
    Tests that we properly log the contents of a scenario file when the 'scenario/'
    prefix is not specified
    """

    pytest.xfail()

    api_base = tests.integration.API_BASE

    resp = requests.post(f"{api_base}/ic", json={"filename": "8.SCN"})
    assert resp.status_code == 200, "Expected the scenario to be loaded"

    resp = requests.get(f"{api_base}/eplog")
    assert resp.status_code == 200, "Expected the episode log to be returned"

    assert not any(
        "FileNotFoundError" in line for line in resp.json()["lines"]
    ), "Expected the log file to contain the scenario content"
