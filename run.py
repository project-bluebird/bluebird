"""
Entry point for the BlueBird app
"""

from bluebird import BlueBird, settings

if __name__ == '__main__':

	# Change any settings if required, can also parse from CLI args
	# settings.BS_HOST = '0.0.0.0'

	# Connect the BlueSky client
	connected = BlueBird.client_connect()

	if connected:
		# Run the Flask app. Blocks here until it exits
		BlueBird.run_app()
	else:
		print('Failed to connect to BlueSky server, exiting')

	BlueBird.stop()
