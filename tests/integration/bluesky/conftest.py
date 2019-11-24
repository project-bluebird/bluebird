"""
Configuration for BlueSky integration tests
"""

import time

import pytest
import requests

from tests.integration import API_URL_BASE

PYTEST_PLUGINS = ["docker_compose"]

MAX_WAIT_SECONDS = 20


@pytest.fixture(scope="function", autouse=True)
def containers(function_scoped_container_getter):
    """
    Wait for the test containers to be available before continuing. Depends on the
    function_scoped_container_getter fixture, to ensure that the containers are started
    first
    """

    timeout = time.time() + MAX_WAIT_SECONDS

    while True:
        try:
            if requests.post(f"{API_URL_BASE}/reset").status_code == 200:
                break
        except requests.exceptions.ConnectionError:
            pass

        if time.time() > timeout:
            raise requests.exceptions.ConnectionError(
                "Couldn't connect to containers before the timeout"
            )

        time.sleep(1)
