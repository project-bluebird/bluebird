from http import HTTPStatus

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
        "gspd": 1,
    }

    resp = requests.post(f"{api_base}/cre", json=data)
    assert resp.status_code == HTTPStatus.CREATED, "Expected aircraft to be created"

    resp = requests.get(f"{api_base}/pos")
    assert resp.status_code == HTTPStatus.OK, "Expected to get the aircraft position"
    assert resp.json() == {
        "TST1001": {
            "actype": "B744",
            "cleared_fl": None,
            "current_fl": 25000,
            "gs": 1,
            "hdg": 0,
            "lat": 0.0,
            "lon": 0.0,
            "requested_fl": None,
            "vs": 0,
        },
        "scenario_time": 0.0,
    }

    resp = requests.get(f"{api_base}/listroute?callsign=TST1001")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert resp.content.decode() == "Aircraft has no route"
