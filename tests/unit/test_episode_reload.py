"""
Tests for the episode log reloading feature
"""

# pylint: disable=redefined-outer-name, unused-argument, no-member

import os

import bluebird.client as bb_client
from bluebird.api.resources.utils import parse_lines
from . import API_PREFIX


def test_parse_lines():
	"""
	Tests the parsing of lines in an episode log
	:return:
	"""

	lines = []
	assert isinstance(parse_lines(lines), str), 'Expected an error response'

	lines = ['aaaaaa']
	assert isinstance(parse_lines(lines), str), 'Expected an error response'

	lines = ['2019-07-11 10:18:28 E Episode started. SIM_LOG_RATE is 0.2 Hz. Seed is None']
	err = parse_lines(lines)
	assert isinstance(err, str), 'Expected an error response'
	assert err == 'Episode seed was not set', 'Expected an error regarding the seed not being set'

	lines = ['2019-07-11 10:18:28 E Episode started. SIM_LOG_RATE is 0.2 Hz. Seed is 1234']
	assert isinstance(parse_lines(lines), str), 'Expected an error response'

	lines.append('ignored')
	lines.append(r'2019-07-11 10:18:29 E Scenario file loaded: scenario\TEST.scn. Contents are:')
	assert isinstance(parse_lines(lines), str), 'Expected an error response'

	lines.append('2019-07-11 10:18:29 E 00:00:00.00>CRE Kl204,B744,52,4,90,FL250,350')
	lines.append('2019-07-11 10:18:29 E 00:00:00.50>DEST KL204,EDDF')

	endline = '2019-07-11 10:21:07 E Episode finished (sim reset)'
	lines.append(endline)

	data = parse_lines(lines)
	assert isinstance(data, dict), 'Expected some data'
	assert data['seed'] == 1234, 'Expected the seed to be set'
	assert len(data['lines']) == 2, 'Expected 2 lines'
	assert data['lines'][0] == '00:00:00.00>CRE Kl204,B744,52,4,90,FL250,350'
	assert data['lines'][1] == '00:00:00.50>DEST KL204,EDDF'

	lines.pop()

	lines.append('2019-07-11 10:18:31 A [2] {data}')
	lines.append('2019-07-11 10:18:31 A [7] {data}')
	assert isinstance(parse_lines(lines), str), 'Expected an error response'

	lines.append('2019-07-11 10:19:47 C [78] ALT KL204 9144')
	lines.append('2019-07-11 10:20:08 C [99] ALT KL204 6096')
	assert isinstance(parse_lines(lines), str), 'Expected an error response'

	lines.append(endline)
	data = parse_lines(lines)
	assert isinstance(data, dict), 'Expected some data'
	assert len(data['lines']) == 4, 'Expected some more commands'
	assert data['lines'][2] == '00:01:18> ALT KL204 9144'
	assert data['lines'][3] == '00:01:39> ALT KL204 6096'


def test_parse_lines_time():
	"""
	Test commands after target time are ignored
	:return:
	"""

	lines = ['2019-07-11 10:18:28 E Episode started. SIM_LOG_RATE is 0.2 Hz. Seed is 1234',
	         'unused',
	         'unused',
	         'unused',
	         r'2019-07-11 10:18:29 E Scenario file loaded: scenario\TEST.scn. Contents are:',
	         '2019-07-11 10:18:29 E 00:00:00.00>CRE Kl204,B744,52,4,90,FL250,350',
	         '2019-07-11 10:18:29 E 00:00:00.50>DEST KL204,EDDF',
	         '2019-07-11 10:19:47 C [78] ALT KL204 9144',
	         '2019-07-11 10:20:08 C [100] ALT KL204 6096',
	         '2019-07-11 10:21:07 E Episode finished (sim reset)']

	data = parse_lines(lines, 99)
	assert isinstance(data, dict), 'Expected data'
	assert len(data['lines']) == 3, 'Expected 3 commands'
	assert 'ALT KL204 9144' in data['lines'][-1], ''


def test_log_reload_from_lines(client, patch_client_sim):
	"""
	Tests the episode reloading given a full logfile in the request
	:param client:
	:param patch_client_sim:
	:return:
	"""

	resp = client.post(API_PREFIX + '/simmode', json={'mode': 'agent'})
	assert resp.status_code == 200, 'Expected the mode to be agent'

	resp = client.post(API_PREFIX + '/seed', json={'value': 1234})
	assert resp.status_code == 200, 'Expected the seed to be set'

	test_file = 'tests/unit/testEpisode.log'
	assert os.path.isfile(test_file), ''
	lines = tuple(open(test_file, 'r'))

	data = {'lines': lines, 'time': 123}
	resp = client.post(API_PREFIX + '/loadlog', json=data)
	assert resp.status_code == 200, 'Expected a 200'


def test_log_reload_from_file(client, patch_client_sim):
	"""
	Tests that the episode reloading works when given a logfile
	:param client:
	:param patch_client_sim:
	:return:
	"""

	resp = client.post(API_PREFIX + '/simmode', json={'mode': 'agent'})
	assert resp.status_code == 200, 'Expected the mode to be agent'

	resp = client.post(API_PREFIX + '/seed', json={'value': 1234})
	assert resp.status_code == 200, 'Expected the seed to be set'

	data = {'filename': 'tests/unit/testEpisode.log', 'time': 123}
	resp = client.post(API_PREFIX + '/loadlog', json=data)
	assert resp.status_code == 200, 'Expected a 200'


def test_log_reload_full(client, patch_client_sim):
	"""
	Tests the full functionality of the log reloading
	:param client:
	:param patch_client_sim:
	:return:
	"""

	resp = client.post(API_PREFIX + '/simmode', json={'mode': 'agent'})
	assert resp.status_code == 200, 'Expected the mode to be agent'

	resp = client.post(API_PREFIX + '/seed', json={'value': 1234})
	assert resp.status_code == 200, 'Expected the seed to be set'

	logfile = 'tests/unit/testEpisode.log'

	data = {'filename': logfile, 'time': -1}
	resp = client.post(API_PREFIX + '/loadlog', json=data)
	assert resp.status_code == 400, 'Expected a 400 due to invalid time'

	data['time'] = 120
	resp = client.post(API_PREFIX + '/loadlog', json=data)
	assert resp.status_code == 200, 'Expected a 200'

	assert bb_client.CLIENT_SIM.was_reset, 'Expected that the simulator was reset'
	assert bb_client.CLIENT_SIM.seed == 5678, 'Expected that the seed was set'
	assert bb_client.CLIENT_SIM.scn_uploaded, 'Expected that the scenario was uploaded'
	assert bb_client.CLIENT_SIM.last_scenario, 'Expected that the scenario was started'
	assert bb_client.CLIENT_SIM.was_stepped, 'Expected that the simulation was stepped'
