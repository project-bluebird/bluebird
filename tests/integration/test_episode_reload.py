"""
Tests for the episode reloading
"""

import requests
import time
from pyproj import Geod

from tests.integration import API_URL_BASE

_WGS84 = Geod(ellps='WGS84')
_ONE_NM = 1852  # Meters


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

	for _ in range(3):
		resp = requests.post(f'{API_URL_BASE}/step')
		assert resp.status_code == 200, 'Expected the simulation was stepped'

	test_acid = 'KL204'

	resp = requests.get(f'{API_URL_BASE}/pos?acid={test_acid}')
	assert resp.status_code == 200, 'Expected to get the aircraft position'

	initial_t = resp.json()['sim_t']
	initial_pos = resp.json()[test_acid]

	resp = requests.post(f'{API_URL_BASE}/alt', json={'acid': test_acid, 'alt': 'FL100'})
	assert resp.status_code == 200, 'Expected to get the aircraft position'

	for _ in range(5):
		resp = requests.post(f'{API_URL_BASE}/step')
		assert resp.status_code == 200, 'Expected the simulation was stepped'

	resp = requests.get(f'{API_URL_BASE}/eplog')
	assert resp.status_code == 200, 'Expected to receive the episode log'

	episode_file = resp.json()['cur_ep_file']
	target_t = 60

	data = {'filename': episode_file, 'time': target_t}

	start = time.time()
	resp = requests.post(f'{API_URL_BASE}/loadlog', json=data)
	print(f'\n! Time for reload: {time.time() - start}')

	assert resp.status_code == 200, 'Expected the simulation was reloaded'

	resp = requests.get(f'{API_URL_BASE}/pos?acid={test_acid}')
	assert resp.status_code == 200, 'Expected to get the aircraft position'

	reloaded_t = resp.json()['sim_t']
	reloaded_pos = resp.json()[test_acid]

	assert reloaded_t == target_t, 'Expected the reloaded time to be at the target'

	_, _, horizontal_sep_m = _WGS84.inv(initial_pos['lon'], initial_pos['lat'],
	                                    reloaded_pos['lon'], reloaded_pos['lat'])
	horizontal_sep_nm = round(horizontal_sep_m / _ONE_NM)

	# TODO Check the deltas are reasonable...
	assert horizontal_sep_nm <= 10, 'Expected positions to roughly match'
	assert abs(reloaded_pos['alt'] - initial_pos['alt']) <= 100 / _ONE_NM, \
		'Expected altitudes to roughly match'
	assert abs(reloaded_pos['gs'] - initial_pos['gs']) <= 50, \
		'Expected ground speeds to roughly match'
	assert abs(reloaded_pos['vs'] - initial_pos['vs']) <= 50, \
		'Expected vertical speeds to roughly match'
