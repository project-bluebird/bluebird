"""
Provides fixtures for integration tests
"""

import os
import subprocess
import time

import pytest
import requests
from dotenv import load_dotenv

MAX_RETRY_ATTEMPTS = 10


@pytest.fixture(scope='function', autouse=True)
def fixture_wait_for_containers(docker_network_info):  # pylint: disable=unused-argument
	"""
	Wait for the test containers to be available before continuing. Depends on the
	docker_network_info fixture, to ensure that the containers are started first
	:param docker_network_info:
	:return:
	"""

	n_failed = 0
	while True:
		try:
			requests.get('http://localhost:5001')
			break
		except requests.exceptions.ConnectionError:
			n_failed += 1
			if n_failed >= MAX_RETRY_ATTEMPTS:
				raise requests.exceptions.ConnectionError('Couldn\'t connect to containers after timeout')
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
		pytest.exit('Docker not detected')
