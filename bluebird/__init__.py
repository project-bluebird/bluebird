from bluebird.cache import CommandCache, StreamCache

# Singletons
APP = None
API = None
CLIENT = None
LOGGER = None

CMD_CACHE = CommandCache()
STM_CACHE = StreamCache()

import bluebird.api
import bluebird.client
from bluebird import settings


def init():
    print("BlueBird init")

    global API, APP, LOGGER
    APP = api.app
    API = api.api
    LOGGER = APP.logger

    global CLIENT
    CLIENT = client.ApiClient()


def client_connect():
    CLIENT.connect(hostname=settings.BS_HOST,
                   event_port=settings.BS_EVENT_PORT,
                   stream_port=settings.BS_STREAM_PORT)


def run_app():

    # Starts the Flask app
    APP.run(host='0.0.0.0', port=80, debug=True)

    # Called when the Flask app exists
    CLIENT.close()
