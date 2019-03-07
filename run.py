"""
Entry point for the BlueBird app
"""

import argparse

from bluebird import BlueBird, settings

if __name__ == '__main__':

	PARSER = argparse.ArgumentParser()
	PARSER.add_argument('--bluesky_host', type=str, help='Hostname of the BlueSky simulation to '
	                                                     'connect to', default='0.0.0.0')
	PARSER.add_argument('--reset_sim', action='store_true', help='Reset the simulation on '
	                                                             'connection')
	ARGS = PARSER.parse_args()
	settings.BS_HOST = ARGS.bluesky_host

	# Connect the BlueSky client
	CONNECTED = BlueBird.client_connect(ARGS.reset_sim)

	if CONNECTED:
		# Run the Flask app. Blocks here until it exits
		BlueBird.run_app()

	BlueBird.stop()
