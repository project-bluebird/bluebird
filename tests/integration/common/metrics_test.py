"""
Integration tests for the metrics endpoints with BlueSky
"""

import pytest
import requests

import tests.integration


def test_metrics_api_basic():
    """Basic integration test for the metrics API endpoint"""

    pytest.xfail()

    api_base = tests.integration.API_BASE

    resp = requests.post(f"{api_base}/simmode", json={"mode": "agent"})
    assert resp.status_code == 200, "Expected the mode to be set"

    resp = requests.post(f"{api_base}/ic", json={"filename": "8.SCN"})
    assert resp.status_code == 200, "Expected the scenario to be loaded"

    resp = requests.get(
        f"{api_base}/metric?name=aircraft_separation&args=SCN1001,SCN1001"
    )
    assert resp.status_code == 200, "Expected valid args to return 200"
    assert resp.json()["aircraft_separation"] == -1, "Expected -1"
