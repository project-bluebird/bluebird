"""
Entry point for the BlueBird app
"""

import os

import argparse
from dotenv import load_dotenv
from semver import VersionInfo

from bluebird import BlueBird, settings


def _parse_args():
	"""
	Parse CLI arguments and override any default settings
	:return:
	"""

	parser = argparse.ArgumentParser()
	parser.add_argument('--sim-type', type=str,
	                    help=f'The type of simulator to connect to. Supported values are: '
	                         f'{", ".join([x.name for x in settings.SimType])}')
	parser.add_argument('--sim-host', type=str, help='Hostname or IP of the simulation to '
	                                                 'connect to')
	parser.add_argument('--reset-sim', action='store_true', help='Reset the simulation on '
	                                                             'connection')
	parser.add_argument('--log-rate', type=float, help='Log rate in sim-seconds')
	parser.add_argument('--sim-mode', type=str, help='Set the initial mode')
	args = parser.parse_args()

	if args.sim_type:
		settings.SIM_TYPE = settings.SimType(args.sim_type)

	if args.sim_host:
		settings.SIM_HOST = args.sim_host

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

	return args


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

	args = _parse_args()
	load_dotenv(verbose=True, override=True)

	if settings.SIM_TYPE == settings.SimType.BlueSky:
		min_sim_version = _get_min_bs_version()
	else:
		# TODO Need to check version of MachColl
		min_sim_version = VersionInfo.parse('0.0.0')

	with BlueBird() as app:
		if app.connect_to_sim(min_sim_version, args.reset_sim):
			# Run the Flask app. Blocks here until it exits
			app.run()


if __name__ == '__main__':
	main()
