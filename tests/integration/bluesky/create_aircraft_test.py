import pytest
import requests

import tests.integration


def test_create_aircraft():

    api_base = tests.integration.API_BASE

    resp = requests.get(f"{api_base}/pos")
    assert resp.status_code == 400, "Expected no aircraft in the simulation"

    data = {
      "callsign": "TST1001",
      "type": "B744",
      "lat": "0",
      "lon": "0",
      "hdg": 0,
      "alt": "FL250",
      "gspd": 1
    }

    resp = requests.post(f"{api_base}/cre", json=data)
    assert resp.status_code == 201, "Expected aircraft to be created"

    resp = requests.get(f"{api_base}/pos")
    assert resp.status_code == 200, "Expected to get the aircraft position"

    # TODO: test response content
