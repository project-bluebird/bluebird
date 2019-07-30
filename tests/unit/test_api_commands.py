"""
Tests each of the API endpoints.

Provides a Flask test_client fixture which is generated from the BlueBird app definition. This
is then used to test the app endpoints with various HTTP requests. Test aircraft data is manually
defined, so we don't have any test dependencies on BlueSky.
"""

# pylint: disable=redefined-outer-name, unused-argument, no-member

import os

import bluebird.client as bb
import bluebird.settings as settings
from bluebird.cache import AC_DATA
from . import API_PREFIX, SIM_DATA, TEST_ACIDS, TEST_DATA, TEST_DATA_KEYS


def test_pos_command(client):
	"""
	Tests the /pos endpoint
	:param client:
	:return:
	"""

	resp = client.get(API_PREFIX + '/pos')
	assert resp.status == '400 BAD REQUEST'

	resp = client.get(API_PREFIX + '/pos', json={'acid': 'TST1001'})
	assert resp.status == '400 BAD REQUEST'

	resp = client.get(API_PREFIX + '/pos?acid=unknown')
	assert resp.status == '404 NOT FOUND'

	for idx in range(len(TEST_DATA['id'])):
		acid = TEST_DATA['id'][idx]

		resp = client.get(API_PREFIX + '/pos?acid={}'.format(acid))
		assert resp.status == '200 OK'

		resp_json = resp.get_json()

		assert len(resp_json) == 2
		assert SIM_DATA[2] == resp_json['sim_t']

		ac_data = resp_json[acid]

		assert len(ac_data) == len(TEST_DATA) - 1  # 'id' not included in response
		assert set(ac_data.keys()) == set(TEST_DATA_KEYS)

		for prop in ac_data:
			assert TEST_DATA[prop][idx] == ac_data[prop]


def test_ic_command(client, patch_client_sim):
	"""
	Tests the /ic endpoint
	:param client:
	:param patch_client_sim:
	:return:
	"""

	resp = client.post(API_PREFIX + '/ic')
	assert resp.status == '400 BAD REQUEST'

	resp = client.post(API_PREFIX + '/ic', json={})
	assert resp.status == '400 BAD REQUEST'

	filename = 'testeroni.scn'

	resp = client.post(API_PREFIX + '/ic', json={'filename': filename})
	assert resp.status == '200 OK'

	assert bb.CLIENT_SIM.last_scenario == filename, 'Expected the filename to be loaded'

	filename = 'testeroni.SCN'

	resp = client.post(API_PREFIX + '/ic', json={'filename': filename})
	assert resp.status == '200 OK'

	assert bb.CLIENT_SIM.last_scenario == filename, 'Expected the filename to be loaded'


def test_reset_command(client, patch_client_sim):
	"""
	Tests the /reset endpoint
	:param client:
	:param patch_client_sim:
	:return:
	"""

	resp = client.post(API_PREFIX + '/reset')
	assert resp.status == '200 OK'

	assert bb.CLIENT_SIM.was_reset, 'Expected the client simulation to be reset'


def test_cre_new_aircraft(client, patch_client_sim):
	"""
	Test the CRE endpoint handles new aircraft correctly
	:param client:
	:param patch_client_sim:
	:return:
	"""

	acid = 'TST1234'
	assert not AC_DATA.contains(acid), 'Expected the test aircraft not to exist'

	cre_data = {'acid': acid, 'type': 'testeroni', 'lat': 0, 'lon': 0, 'hdg': 0, 'alt': 0, 'spd': 0}
	resp = client.post(API_PREFIX + '/cre', json=cre_data)

	assert resp.status == '201 CREATED'


def test_cre_existing_aircraft(client, patch_client_sim):
	"""
	Test the CRE endpoint handles existing aircraft correctly
	:param client:
	:param patch_client_sim:
	:return:
	"""

	acid = TEST_ACIDS[0]
	assert AC_DATA.get(acid) is not None, 'Expected the test aircraft to exist'

	cre_data = {'acid': acid, 'type': 'testeroni', 'lat': 0, 'lon': 0, 'hdg': 0, 'alt': 0, 'spd': 0}
	resp = client.post(API_PREFIX + '/cre', json=cre_data)

	assert resp.status == '400 BAD REQUEST'


def test_scenario_endpoint(client, patch_client_sim):
	"""
	Tests the create scenario endpoint
	:param client:
	:param patch_client_sim:
	:return:
	"""

	resp = client.post(API_PREFIX + '/scenario')
	assert resp.status == '400 BAD REQUEST'

	data = {'scn_name': 'new-scenario', 'content': []}

	resp = client.post(API_PREFIX + '/scenario', json=data)
	assert resp.status == '400 BAD REQUEST'

	data['content'] = ['invalid', 'invalid']

	resp = client.post(API_PREFIX + '/scenario', json=data)
	assert resp.status == '400 BAD REQUEST'

	data['content'] = ['00:00:00>CRE TEST A320 0 0 0 0', '00:00:00 > CRE TEST A320 0 0 0 0']

	resp = client.post(API_PREFIX + '/scenario', json=data)
	assert resp.status == '201 CREATED'

	data['start_new'] = True
	data['start_dtmult'] = 1.23

	resp = client.post(API_PREFIX + '/scenario', json=data)
	assert resp.status == '200 OK'

	assert bb.CLIENT_SIM.last_scenario == 'new-scenario.scn', 'Expected the filename to be loaded'
	assert bb.CLIENT_SIM.last_dtmult == 1.23, 'Expected the dtmult to be set'

	# Remove the test file from the BlueSky submodule
	try:
		os.remove('bluesky/scenario/new-scenario.scn')
	except OSError:
		pass


def test_change_mode(client, patch_client_sim):
	"""
	Tests the functionality of the simmode endpoint
	:param client:
	:param patch_client_sim:
	:return:
	"""

	assert settings.SIM_MODE == 'sandbox', 'Expected the initial mode to be sandbox'

	data = {'mode': 'test'}
	resp = client.post(API_PREFIX + '/simmode', json=data)

	assert resp.status == '400 BAD REQUEST', 'Expected an invalid mode to return 400'

	data['mode'] = 'agent'
	resp = client.post(API_PREFIX + '/simmode', json=data)

	assert resp.status == '200 OK', 'Expected a valid mode to return 200'
	assert settings.SIM_MODE == 'agent', 'Expected the final mode to be agent'


def test_non_agent_mode_step(client, patch_client_sim):
	"""
	Tests that the sim is not stepped if in the sandbox mode
	:param client:
	:param patch_client_sim:
	:return:
	"""

	client.post(API_PREFIX + '/simmode', json={'mode': 'sandbox'})
	assert settings.SIM_MODE == 'sandbox', 'Expected the initial mode to be sandbox'

	resp = client.post(f'{API_PREFIX}/step')
	assert resp.status_code == 400, 'Expected a 400 BAD REQUEST'
	assert not bb.CLIENT_SIM.was_stepped, 'Expected the simulation was not stepped forward'


def test_agent_mode_step(client, patch_client_sim):
	"""
	Tests that the sim is stepped if in agent mode
	:param client:
	:param patch_client_sim:
	:return:
	"""

	client.post(API_PREFIX + '/simmode', json={'mode': 'agent'})
	assert settings.SIM_MODE == 'agent', 'Expected the mode to be agent'

	resp = client.post(f'{API_PREFIX}/step')
	assert resp.status_code == 200, 'Expected a 200 response'
	assert bb.CLIENT_SIM.was_stepped, 'Expected the simulation was stepped forward'


def test_set_seed(client, patch_client_sim):
	"""
	Tests the functionality of the seed endpoint
	:param client:
	:param patch_client_sim:
	:return:
	"""

	resp = client.post(API_PREFIX + '/seed')
	assert resp.status == '400 BAD REQUEST'

	data = {'test': 1234}

	resp = client.post(API_PREFIX + '/seed', json=data)
	assert resp.status == '400 BAD REQUEST'

	data = {'value': 'test'}

	resp = client.post(API_PREFIX + '/seed', json=data)
	assert resp.status == '400 BAD REQUEST'

	data = {'value': -123}

	resp = client.post(API_PREFIX + '/seed', json=data)
	assert resp.status == '400 BAD REQUEST'

	data = {'value': 123}

	resp = client.post(API_PREFIX + '/seed', json=data)
	assert resp.status == '200 OK'
	assert bb.CLIENT_SIM.seed == 123, ''

	data = {'value': 2 ** 32 - 1}
	resp = client.post(API_PREFIX + '/seed', json=data)
	assert resp.status == '200 OK'

	data = {'value': 2 ** 32}
	resp = client.post(API_PREFIX + '/seed', json=data)
	assert resp.status == '400 BAD REQUEST'


def test_alt_fl_parsing(client, patch_client_sim):
	"""
	Tests that we correctly parse FL to meters in the ALT endpoint
	:return:
	"""

	acid = TEST_ACIDS[0]
	data = {'acid': acid, 'alt': 'FL120'}

	resp = client.post(API_PREFIX + '/alt', json=data)
	assert resp.status_code == 200, 'Expected OK'
	assert bb.CLIENT_SIM.last_stack_cmd == 'ALT TST1001 3658', 'Expected ALT to match'

	data['alt'] = '12345'

	resp = client.post(API_PREFIX + '/alt', json=data)
	assert resp.status_code == 200, 'Expected OK'
	assert bb.CLIENT_SIM.last_stack_cmd == 'ALT TST1001 12345', 'Expected ALT to match'
