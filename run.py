
import sys

import bluebird as bb

if __name__ == '__main__':

    # Initialise the various modules
    bb.init()

    # Connect the BlueSky client
    try:
        bb.client_connect()
    except TimeoutError as e:
        print('Failed to connect to BlueSky server: {}'.format(e))
        bb.stop()
        sys.exit(0)

    # Run the Flask app
    bb.run_app()
