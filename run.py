"""
Entry point for the BlueBird app
"""

import json
import os

import argparse
from dotenv import load_dotenv
from semver import VersionInfo

from bluebird import BlueBird, settings


def _parse_args():
	"""
	Parse cli arguments and override any BlueBird settings
	:return:
	"""

	# TODO Add verb for selecting bluesky/nats sim. Default to bluesky if not specified

	parser = argparse.ArgumentParser()
	parser.add_argument('--bluesky_host', type=str, help='Hostname of the BlueSky simulation to '
	                                                     'connect to')
	parser.add_argument('--reset_sim', action='store_true', help='Reset the simulation on '
	                                                             'connection')
	parser.add_argument('--log_rate', type=float, help='Log rate in sim-seconds')
	parser.add_argument('--sim_mode', type=str, help='Set the initial mode')
	parser.add_argument('--sectors', type=str, help='Loads sectors from the specified file')
	args = parser.parse_args()

	if args.bluesky_host:
		settings.BS_HOST = args.bluesky_host

	if args.log_rate:
		if args.log_rate > 0:
			settings.SIM_LOG_RATE = args.log_rate
		else:
			raise ValueError('Rate must be positive')

	mode = args.sim_mode
	if mode:
		if not mode in settings.SIM_MODES:
			available = ', '.join(settings.SIM_MODES)
			raise ValueError(f'Mode \'{mode}\' not supported. Must be one of: {available}')
		settings.SIM_MODE = mode

	if args.sectors:
		settings.SECTORS = _load_sector_data(args.sectors)

	return args

def _load_sector_data(filename) -> list:
	"""
	Load sector data from a given file

	:param filename:
	:return:
	:rtype: list
	"""

	with open(filename) as file:
		data = json.load(file)

	for sector in data['sectors']:
		if not all(k in sector for k in settings.SECTOR_KEYS):
			raise ValueError('Missing key in sector data')

	return data['sectors']

def _get_min_bs_version():
	bs_min_version = os.getenv('BS_MIN_VERSION')
	if not bs_min_version:
		raise ValueError('Error: the BS_MIN_VERSION environment variable must be set')
	return VersionInfo.parse(bs_min_version)


def main():
	"""
	Main app entry point
	:return:
	"""

	load_dotenv(verbose=True, override=True)
	bs_min_version = _get_min_bs_version()

	args = _parse_args()

	with BlueBird() as app:
		if app.client_connect(bs_min_version, args.reset_sim):
			# Run the Flask app. Blocks here until it exits. Note - any code after this
			# exits might not be executed
			app.run()


if __name__ == '__main__':
	main()
