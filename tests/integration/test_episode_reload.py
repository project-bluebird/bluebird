"""
Tests for the episode reloading
"""

import requests

from tests.integration import API_URL_BASE
import time


def test_episode_reload_basic():
	"""
	Tests the basic functionality of the episode reloading
	:return:
	"""

	resp = requests.post(f'{API_URL_BASE}/simmode', json={'mode': 'agent'})
	assert resp.status_code == 200, 'Expected the mode to be set'

	resp = requests.post(f'{API_URL_BASE}/seed', json={'value': 123123})
	assert resp.status_code == 200, 'Expected that the seed was set'

	resp = requests.post(f'{API_URL_BASE}/ic', json={'filename': 'TEST.scn'})
	assert resp.status_code == 200, 'Expected that the scenario was loaded'

	resp = requests.post(f'{API_URL_BASE}/dtmult', json={'multiplier': 20})
	assert resp.status_code == 200, 'Expected DTMULT to be set'

	for _ in range(5):
		resp = requests.post(f'{API_URL_BASE}/step')
		assert resp.status_code == 200, 'Expected the simulation was stepped'

	test_acid = 'KL204'

	resp = requests.post(f'{API_URL_BASE}/alt', json={'acid': test_acid, 'alt': 'FL100'})
	assert resp.status_code == 200, 'Expected to get the aircraft position'

	for _ in range(5):
		resp = requests.post(f'{API_URL_BASE}/step')
		assert resp.status_code == 200, 'Expected the simulation was stepped'

	resp = requests.get(f'{API_URL_BASE}/pos?acid={test_acid}')
	assert resp.status_code == 200, 'Expected to get the aircraft position'

	initial_t = resp.json()['sim_t']
	initial_pos = resp.json()[test_acid]

	resp = requests.get(f'{API_URL_BASE}/eplog')
	assert resp.status_code == 200, 'Expected to receive the episode log'

	episode_file = resp.json()['cur_ep_file']
	target_t = 60

	data = {'filename': episode_file, 'time': target_t}
	resp = requests.post(f'{API_URL_BASE}/loadlog', json=data)
	assert resp.status_code == 200, 'Expected the simulation was reloaded'

	print(f'\n! [{initial_t}] {initial_pos}')

	start = time.time()
	resp = requests.get(f'{API_URL_BASE}/pos?acid={test_acid}')
	assert resp.status_code == 200, 'Expected to get the aircraft position'
	print(f'\n! Time for reload: {time.time() - start}')

	reloaded_t = resp.json()['sim_t']
	reloaded_pos = resp.json()[test_acid]

	print(f'\n! [{reloaded_t}] {reloaded_pos}')

	assert reloaded_t == target_t, ''
