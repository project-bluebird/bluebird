"""
Basic "happy path" test for BlueSky
"""

from tests.integration.common.happy_path_test import happy_path


def test_happy_path(containers):
    happy_path()
