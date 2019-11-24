"""
Test for https://github.com/alan-turing-institute/bluebird/issues/62
"""

import pytest
import requests

from tests.integration import API_URL_BASE


def test_issue_62():
    """
    Tests that we properly log the contents of a scenario file when the 'scenario/'
    prefix is not specified
    :return:
    """

    pytest.xfail()

    resp = requests.post(f"{API_URL_BASE}/ic", json={"filename": "8.SCN"})
    assert resp.status_code == 200, "Expected the scenario to be loaded"

    resp = requests.get(f"{API_URL_BASE}/eplog")
    assert resp.status_code == 200, "Expected the episode log to be returned"

    assert not any(
        "FileNotFoundError" in line for line in resp.json()["lines"]
    ), "Expected the log file to contain the scenario content"
