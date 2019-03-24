"""
Entry point for the BlueBird app
"""

import argparse

from bluebird import BlueBird, settings


def parse_args():
	"""
	Parse cli arguments and override any BlueBird settings
	:return:
	"""

	parser = argparse.ArgumentParser()
	parser.add_argument('--bluesky_host', type=str, help='Hostname of the BlueSky simulation to '
	                                                     'connect to')
	parser.add_argument('--reset_sim', action='store_true', help='Reset the simulation on '
	                                                             'connection')
	parser.add_argument('--log_rate', type=float, help='Log rate in sim-seconds')
	args = parser.parse_args()

	settings.BS_HOST = args.bluesky_host

	if args.log_rate:
		if args.log_rate > 0:
			settings.SIM_LOG_RATE = args.log_rate
		else:
			raise ValueError('Rate must be positive')

	return args


def main():
	"""
	Main app entry point
	:return:
	"""

	args = parse_args()

	# Connect the BlueSky client
	connected = BlueBird.client_connect(args.reset_sim)

	if connected:
		# Run the Flask app. Blocks here until it exits
		BlueBird.run_app()

	BlueBird.stop()


if __name__ == '__main__':
	main()
