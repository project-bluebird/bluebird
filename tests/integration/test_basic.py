"""
Initial tests for Docker in Travis CI
"""

import pytest


def test_docker(docker_network_info):
	assert True


def test_skip():
	pytest.skip('Test skip')


@pytest.mark.incremental
class TestBasic:
	"""
	Test for teh incremental decorator. test_shutdown should not run and be marked as 'xFail'
	"""

	def test_start(self):
		pass

	def test_shutdown(self):
		pass
