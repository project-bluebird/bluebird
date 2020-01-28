"""
Provides fixtures for integration tests
"""
# NOTE(rkm 2020-01-28) Some of the setup logic here is a bit tricky, since the tests
# which are requested to be run may not match up with the other options that have been
# specified. I.e. it's possible to request to run the MachColl integration tests but
# and also specify --integration-sim=bluesky.
import importlib
import os
import re
import subprocess
import time
from datetime import datetime
from http import HTTPStatus
from pathlib import Path

import pytest
import requests
from compose.cli.command import project_from_options
from compose.project import Project as ComposeProject
from compose.service import BuildAction
from compose.service import ImageType

import tests.integration
from bluebird.settings import Settings
from tests import API_PREFIX


_HOST_RE = re.compile(r"http:\/\/(.*):.*")

_MAX_WAIT_SECONDS = 30


def _wait_for_bluebird():

    timeout = time.time() + _MAX_WAIT_SECONDS
    reset_api = f"{tests.integration.API_BASE}/reset"

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


@pytest.fixture(scope="package", autouse=True)
def pre_integration_setup(request):
    """Determines if the integration tests can be run, and sets up the containers"""

    should_skip = not (
        os.getenv("CI", "").upper() == "TRUE"
        or request.config.getoption("--run-integration")
    )

    if should_skip:
        pytest.xfail("Not running in CI, and --run-integration not specified")

    command = ["docker", "system", "info"]

    docker_host = request.config.getoption("--docker-host")
    if docker_host:
        command.insert(1, f"-H {docker_host}")

    docker_available = not subprocess.call(
        command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, shell=True,
    )

    if not docker_available:
        pytest.fail("Integration tests specified but Docker not detected")

    integration_sim = request.config.getoption("--integration-sim")

    # Grab and run the pre_integration_check function for the specified simulator
    mod = importlib.import_module(f"{__package__}.{integration_sim}.__init__")
    try:
        pre_integration_check = getattr(mod, "pre_integration_check")
    except AttributeError:
        pytest.exit(
            f"Integration test package for {integration_sim} has no function named "
            "pre_integration_check",
            1,
        )
    pre_integration_check()

    api_host = docker_host.split(":")[0] if docker_host else "localhost"
    api_base = f"http://{api_host}:{Settings.PORT}{API_PREFIX}"
    tests.integration.API_BASE = api_base

    compose_file = Path("tests", "integration", integration_sim, "docker-compose.yml",)

    if not compose_file.exists():
        pytest.exit(f"Couldn't find {compose_file}", 1)

    project = project_from_options(
        project_dir=str(compose_file.parent),
        options={
            "--file": [compose_file.name],
            "--host": docker_host or None,
            "--project-name": "bluebird",
        },
    )

    project.up(do_build=BuildAction.force)

    print("\n=== Integration setup complete ===\n")

    yield project  # Runs all the tests

    project.down(ImageType.none, include_volumes=True, timeout=0)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Makes the test result available to the teardown fixture"""
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def _print_container_logs(project, restart_t):
    for container in reversed(project.containers()):
        header = f"\nLogs from {container.service}:"
        spacer = "\n" + "=" * len(header)
        logs = (
            container.logs(since=restart_t).decode("utf-8", errors="replace")
            or "(no logs)"
        )
        print(f"{header}{spacer}\n{logs}{spacer}")


@pytest.fixture(scope="function", autouse=True)
def integration_test_wrapper(pre_integration_setup, request):
    """Performs setup & teardown around each integration test"""

    # The pre_integration_setup fixture yields the compose project
    project: ComposeProject
    project = pre_integration_setup

    restart_t = datetime.utcnow()

    project.restart(timeout=0)

    try:
        _wait_for_bluebird()
    except requests.exceptions.ConnectionError:
        _print_container_logs(project, restart_t)
        raise

    print(f"\n=== New test ===")

    yield  # Run the test

    # Print the container logs if the test failed
    if request.node.rep_call.failed:
        _print_container_logs(project, restart_t)
