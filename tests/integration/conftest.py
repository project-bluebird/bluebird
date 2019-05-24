"""
Provides fixtures for integration tests
"""

import os

import pytest
import requests
import subprocess
import time
from dotenv import load_dotenv

from tests.integration import API_URL_BASE

MAX_WAIT_SECONDS = 15


@pytest.fixture(scope='function', autouse=True)
def fixture_wait_for_containers(docker_network_info):  # pylint: disable=unused-argument
	"""
	Wait for the test containers to be available before continuing. Depends on the
	docker_network_info fixture, to ensure that the containers are started first
	:param docker_network_info:
	:return:
	"""

	timeout = time.time() + MAX_WAIT_SECONDS

	while True:
		try:
			if requests.post(f'{API_URL_BASE}/reset').status_code == 200:
				break
		except requests.exceptions.ConnectionError:
			pass

		if time.time() > timeout:
			raise requests.exceptions.ConnectionError("Couldn't connect to containers before the "
			                                          "timeout")

		time.sleep(1)


@pytest.fixture(scope='session', autouse=True)
def pre_integration_check(request):
	"""
	Skips all integration tests if not inside a CI environment, unless forced with the CLI option.
	Also checks if Docker is available.
	:param request:
	:return:
	"""

	load_dotenv(verbose=True, override=True)

	should_skip = not (
					os.getenv('CI', '').upper() == 'TRUE' or request.config.getoption("--run-integration"))

	if should_skip:
		pytest.skip('Not running in CI, and --run-integration not specified')

	docker_avail = not subprocess.call(['docker', 'system', 'info'], stdout=subprocess.DEVNULL,
	                                   stderr=subprocess.DEVNULL)

	if not docker_avail:
		pytest.exit('Docker not detected', 1)
