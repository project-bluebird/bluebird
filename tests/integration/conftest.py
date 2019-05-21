"""
Provides fixtures for integration tests
"""

import os
import subprocess

import pytest
from dotenv import load_dotenv


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


def pytest_runtest_makereport(item, call):
	"""
	Mark the current item so the next incremental test will be xFailed
	:param item:
	:param call:
	:return:
	"""

	if 'incremental' in item.keywords:
		if call.excinfo:
			item.parent.previous_failed = True


def pytest_runtest_setup(item):
	"""
	xFail the test if the previous one has failed
	:param item:
	:return:
	"""

	if 'incremental' in item.keywords:
		if getattr(item.parent, 'previous_failed', False):
			pytest.xfail(f'Previous incremental test failed')
