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

	initial_sim_t = resp.json()['sim_t']

	resp = requests.post(f'{API_URL_BASE}/dtmult', json={'multiplier': 5})
	assert resp.status_code == 200, 'Expected DTMULT to be set'

	resp = requests.post(f'{API_URL_BASE}/step')
	assert resp.status_code == 200, 'Expected the simulation was stepped'

	resp = requests.get(f'{API_URL_BASE}/pos?acid=SCN1001')
	assert resp.status_code == 200, 'Expected to get the aircraft position'

	diff = resp.json()['sim_t'] - initial_sim_t
	assert diff == 5, 'Expected the time diff to be 5 seconds'
