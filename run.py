
import bluebird as bb

if __name__ == '__main__':

    # Initialise the various modules
    bb.init()

    # Connect the BlueSky client
    connected = bb.client_connect()

    if connected:
        # Run the Flask app
        bb.run_app()
    else:
        print('Failed to connect to BlueSky server, exiting')

    bb.stop()
