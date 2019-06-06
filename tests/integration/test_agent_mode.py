"""
Tests for the agent mode
"""

import requests

from tests.integration import API_URL_BASE


def test_agent_mode():
    """
    Tests that IC and STEP perform correctly in agent mode with BlueSky
    """

    resp = requests.post(f'{API_URL_BASE}/simmode', json={'mode': 'agent'})
    assert resp.status_code == 200, 'Expected the mode to be set'

    resp = requests.post(f'{API_URL_BASE}/ic', json={'filename': '8.SCN'})
    assert resp.status_code == 200, 'Expected the scenario to be loaded'

    resp = requests.get(f'{API_URL_BASE}/pos?acid=SCN1001')
    assert resp.status_code == 200, 'Expected to get the aircraft position'

    initial_lat = resp.json()['SCN1001']['lat']
    initial_lon = resp.json()['SCN1001']['lon']
    
    resp = requests.post(f'{API_URL_BASE}/dtmult', json={'multiplier': 5})
    assert resp.status_code == 200, 'Expected DTMULT to be set'

    resp = requests.post(f'{API_URL_BASE}/step')
    assert resp.status_code == 200, 'Expected the simulation was stepped'

    resp = requests.get(f'{API_URL_BASE}/pos?acid=SCN1001')
    assert resp.status_code == 200, 'Expected to get the aircraft position'

    new_lat = resp.json()['SCN1001']['lat']
    new_lon = resp.json()['SCN1001']['lon']

    assert new_lat != initial_lat, 'Expected initial and final lat to differ'
    assert new_lon != initial_lon, 'Expected initial and final lon to differ'

