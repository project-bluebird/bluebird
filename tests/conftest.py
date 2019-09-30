"""
Main test configuration
"""

PYTEST_PLUGINS = ["docker_compose"]


def pytest_addoption(parser):
    """
    Add CLI option to force running of integration tests outside of a CI environment
    :param parser:
    :return:
    """

    parser.addoption("--run-integration", action="store_true")
