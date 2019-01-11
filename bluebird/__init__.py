from bluebird.cache import AcDataCache

# TODO Remove these - not very pythonic!
# Singletons
APP = None
API = None
CLIENT = None
TIMERS = []
CACHES = {}

import bluebird.api
import bluebird.client
from bluebird import settings


def init():
    print("BlueBird init")

    global API, APP, LOGGER
    APP = api.app
    API = api.api
    LOGGER = APP.logger

    global CACHES
    CACHES['acdata'] = AcDataCache()

    global CLIENT
    CLIENT = client.ApiClient()


def client_connect():
    try:
        CLIENT.connect(hostname=settings.BS_HOST,
                       event_port=settings.BS_EVENT_PORT,
                       stream_port=settings.BS_STREAM_PORT,
                       timeout=1)
        return True
    except TimeoutError:
        CLIENT.stop()
        return False


def run_app():
    print('Starting Flask app')
    APP.run(host='0.0.0.0', port=80, debug=True)


def stop():
    for item in TIMERS:
        item.stop()
