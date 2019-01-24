"""
Tests each of the API endpoints.

Provides a Flask test_client fixture which is generated from the BlueBird app definition. This
is then used to test the app endpoints with various HTTP requests. Test aircraft data is manually
defined, so we don't have any test dependencies on BlueSky.
"""

# pylint: disable=redefined-outer-name

import pytest

import bluebird.api as bluebird_api
from bluebird import settings
from bluebird.cache import AC_DATA
from bluebird.cache.cache import EXTRAS

API_PREFIX = '/api/v' + str(settings.API_VERSION)

# This is the same format as what BlueSky returns
TEST_DATA = {'id': ['TST1001', 'TST1002'], 'alt': [1234, 5678], 'gs': [123.0, 456.0],
             'lat': [55.945336, 51.529877], 'lon': [-3.187299, -0.127720], 'vs': [4321, 8765]}

TEST_DATA_KEYS = list(TEST_DATA.keys()) + list(EXTRAS.keys())
TEST_DATA_KEYS.remove('id')


@pytest.fixture
def client():
	"""
	Creates a Flask test client for BlueBird
	:return:
	"""

	bluebird_api.FLASK_APP.config['TESTING'] = True
	test_client = bluebird_api.FLASK_APP.test_client()

	assert len({len(x) for x in TEST_DATA.values()}) == 1,\
		'Expected TEST_DATA to contain property arrays of the same length.'

	AC_DATA.fill(TEST_DATA)

	yield test_client


def test_pos_command(client):
	"""
	Tests the /pos endpoint
	:param client:
	:return:
	"""

	resp = client.get(API_PREFIX + '/pos')
	assert resp.status == '400 BAD REQUEST'

	resp = client.get(API_PREFIX + '/pos', json={})
	assert resp.status == '400 BAD REQUEST'

	resp = client.get(API_PREFIX + '/pos', json={'acid': 'unknown'})
	assert resp.status == '404 NOT FOUND'

	for idx in range(len(TEST_DATA['id'])):
		acid = TEST_DATA['id'][idx]

		resp = client.get(API_PREFIX + '/pos', json={'acid': acid})
		assert resp.status == '200 OK'

		resp_json = resp.get_json()
		print('Response JSON: {}'.format(resp_json))

		assert len(resp_json) == len(TEST_DATA)
		assert set(resp_json.keys()) == set(TEST_DATA_KEYS)

		for prop in resp_json:
			if not prop.startswith('_'):
				assert resp_json[prop] == TEST_DATA[prop][idx]
			else:
				assert prop in EXTRAS.keys()
