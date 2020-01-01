"""
Integration tests for BlueSky
"""

import time
from http import HTTPStatus

import requests


MAX_WAIT_SECONDS = 20


def wait_for_containers(api_base):

    timeout = time.time() + MAX_WAIT_SECONDS
    reset_api = f"{api_base}/reset"

    while True:
        try:
            if requests.post(reset_api).status_code == HTTPStatus.OK:
                break
        except requests.exceptions.ConnectionError:
            pass

        if time.time() > timeout:
            raise requests.exceptions.ConnectionError(
                "Couldn't get a response from BlueBird before the timeout"
            )

        time.sleep(1)
