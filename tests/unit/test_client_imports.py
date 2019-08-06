"""
Tests for the simulation client ABC
"""

import importlib


def test_bluesky_sim_client_import():
	"""
	Tests that the default simulation client package can be imported without errors
	:return:
	"""

	mod_path = 'bluebird.simclient.bluesky'
	importlib.import_module(mod_path)


def test_bluesky_sim_client_create():
	"""
	Tests that the default SimClient properly implements AbstractSimClient
	:return:
	"""

	mod_path = 'bluebird.simclient.bluesky.simclient'
	importlib.import_module(mod_path).SimClient(None, None)
