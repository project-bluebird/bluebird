"""
Initial tests for Docker in Travis CI
"""

import requests

from tests.integration import API_URL_BASE


def test_docker_basic():
    """
	Test basic request/response with the BlueBird container
	:return:
	"""

    resp = requests.get(f"{API_URL_BASE}/pos?acid=all")
    assert resp.status_code == 400, "Expected a 400 BAD REQUEST"
