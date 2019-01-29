"""
Tests each of the API endpoints.

Provides a Flask test_client fixture which is generated from the BlueBird app definition. This
is then used to test the app endpoints with various HTTP requests. Test aircraft data is manually
defined, so we don't have any test dependencies on BlueSky.
"""

import pytest

import bluebird.api as bluebird_api
from . import API_PREFIX, EXTRAS, TEST_DATA, TEST_DATA_KEYS


@pytest.fixture
def client():
	"""
	Creates a Flask test client for BlueBird, and populates AC_DATA with the test data
	:return:
	"""

	bluebird_api.FLASK_APP.config['TESTING'] = True
	test_client = bluebird_api.FLASK_APP.test_client()

	yield test_client


# pylint: disable=redefined-outer-name
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

		assert len(resp_json) == len(TEST_DATA)
		assert set(resp_json.keys()) == set(TEST_DATA_KEYS)

		for prop in resp_json:
			if not prop.startswith('_'):
				assert resp_json[prop] == TEST_DATA[prop][idx]
			else:
				assert prop in EXTRAS.keys()
