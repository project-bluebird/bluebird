"""
Test for https://github.com/alan-turing-institute/bluebird/issues/63
"""

import pytest
import requests

from tests.integration import API_URL_BASE


def test_issue_63():
    """
    Tests that a newly uploaded scenario file is properly stored
    :return:
    """

    pytest.xfail()

    scn_data = {
        "scn_name": "issue-63-test",
        "content": [
            "00:00:00>CRE TST63 A320 EHAM RWY18L * 0 0",
            "00:00:01>SPD TST63 300",
            "00:00:01>ALT TST63 FL300",
        ],
        "start_new": True,
    }

    resp = requests.post(f"{API_URL_BASE}/scenario", json=scn_data)
    assert resp.status_code == 200, "Expected the scenario to be uploaded"

    resp = requests.get(f"{API_URL_BASE}/eplog")
    assert resp.status_code == 200, "Expected the episode log to be returned"
    assert resp.json()["cur_ep_file"] is not None, "Expected the episode file to exist"
