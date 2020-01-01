"""
Main test configuration
"""


def pytest_addoption(parser):
    """Add extra CLI options for integration testing"""

    # TODO(RKM 2019-12-31) Update docs
    parser.addoption("--run-integration", action="store_true")
    parser.addoption("--docker-host", action="store", default="localhost")
    parser.addoption("--integration-sim", action="store", default="bluesky")
