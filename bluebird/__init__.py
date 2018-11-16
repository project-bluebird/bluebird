from bluebird.cache import CommandCache, StreamCache

# Singletons
APP = None
API = None
CLIENT = None

CMD_CACHE = CommandCache()
STM_CACHE = StreamCache()

import bluebird.api
import bluebird.client
from bluebird import settings


def init():
    print("BlueBird init")

    global API, APP
    APP = api.app
    API = api.api

    global CLIENT
    CLIENT = client.ApiClient()


def client_connect():
    CLIENT.connect(hostname=settings.BS_HOST,
                   event_port=settings.BS_EVENT_PORT,
                   stream_port=settings.BS_STREAM_PORT)


def run_app():
    APP.run(host='0.0.0.0', port=80, debug=True)
    CLIENT.close()
