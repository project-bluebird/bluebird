"""
Test for https://github.com/alan-turing-institute/bluebird/issues/63
"""
import pytest
import requests

import tests.integration


def test_issue_63():
    """Tests that a newly uploaded scenario file is properly stored"""

    pytest.xfail()

    api_base = tests.integration.API_BASE

    scn_data = {
        "scn_name": "issue-63-test",
        "content": [
            "00:00:00>CRE TST63 A320 EHAM RWY18L * 0 0",
            "00:00:01>SPD TST63 300",
            "00:00:01>ALT TST63 FL300",
        ],
        "start_new": True,
    }

    resp = requests.post(f"{api_base}/scenario", json=scn_data)
    assert resp.status_code == 200, "Expected the scenario to be uploaded"

    resp = requests.get(f"{api_base}/eplog")
    assert resp.status_code == 200, "Expected the episode log to be returned"
    assert resp.json()["cur_ep_file"] is not None, "Expected the episode file to exist"
