import bluebird as bb

if __name__ == '__main__':
    # Initialise the various modules
    bb.init()

    # Connect the BlueSky client
    bb.client_connect()

    # Run the Flask app
    bb.run_app()
