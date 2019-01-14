"""
Entry point for the BlueBird app
"""

import argparse

from bluebird import BlueBird, settings

if __name__ == '__main__':

	parser = argparse.ArgumentParser()
	parser.add_argument('--bluesky_host', type=str, help='', default='0.0.0.0')
	args = parser.parse_args()
	settings.BS_HOST = args.bluesky_host

	# Connect the BlueSky client
	connected = BlueBird.client_connect()

	if connected:
		# Run the Flask app. Blocks here until it exits
		BlueBird.run_app()

	BlueBird.stop()
