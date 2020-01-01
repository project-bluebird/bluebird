"""
Configuration for MachColl integration tests
"""

import pytest


def ignore_other_tests(request):
    integration_sim = request.config.getoption("--integration-sim")
    if integration_sim.lower() != "machcoll":
        pytest.skip()
