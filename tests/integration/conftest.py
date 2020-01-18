"""
Provides fixtures for integration tests
"""
import functools
import importlib
import os
import re
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Callable

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


@pytest.fixture(scope="session", autouse=True)
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
        pytest.exit("Docker not detected", 1)

    integration_sim = request.config.getoption("--integration-sim")

    # Grab the wait_for_containers function so we can use it later
    mod = importlib.import_module(f"{__package__}.{integration_sim}.__init__")
    try:
        wait_for_containers = getattr(mod, "wait_for_containers")
    except AttributeError:
        pytest.exit(
            f"Inegration test package for {integration_sim} has no function named "
            "wait_for_containers",
            1,
        )

    api_host = docker_host.split(":")[0] if docker_host else "localhost"
    api_base = f"http://{api_host}:{Settings.PORT}{API_PREFIX}"
    tests.integration.API_BASE = api_base

    # Bind the base API URL to the wait_for_containers function so we don't have to pass
    # it around
    wait_for_containers = functools.partial(wait_for_containers, api_base)

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

    yield (project, wait_for_containers)  # Runs all the tests

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

    # The pre_integration_setup fixture yields the compose project, and the
    # wait_for_containers function
    project: ComposeProject
    wait_for_containers: Callable
    project, wait_for_containers = pre_integration_setup

    restart_t = datetime.utcnow()

    project.restart(timeout=0)

    try:
        wait_for_containers()
    except requests.exceptions.ConnectionError:
        _print_container_logs(project, restart_t)
        raise

    print(f"\n=== New test ===")

    yield  # Run the test

    # Print the container logs if the test failed
    if request.node.rep_call.failed:
        _print_container_logs(project, restart_t)
