"""
Provides fixtures for integration tests
"""

import os
import subprocess

import pytest


@pytest.fixture(scope="session", autouse=True)
def pre_integration_check(request):
    """
    Skips all integration tests if not inside a CI environment, unless forced with the
    CLI option. Also checks if Docker is available.
    :param request:
    :return:
    """

    # load_dotenv(verbose=True, override=True)

    should_skip = not (
        os.getenv("CI", "").upper() == "TRUE"
        or request.config.getoption("--run-integration")
    )

    if should_skip:
        pytest.xfail("Not running in CI, and --run-integration not specified")

    docker_avail = not subprocess.call(
        ["docker", "system", "info"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    if not docker_avail:
        pytest.exit("Docker not detected", 1)
