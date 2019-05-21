"""
Initial tests for Docker in Travis CI
"""

import requests

URL_BASE = 'http://localhost:5001/api/v1/'


def test_docker_basic():
	"""
	Test basic request/response with the BlueBird container
	:return:
	"""

	resp = requests.get(URL_BASE + 'pos?acid=all')
	assert resp.status_code == 400, 'Expected a 400 BAD REQUEST'
