"""
Basic "happy path" test for BlueSky
"""
from datetime import datetime

from tests.integration.common.happy_path_test import run_happy_path
from tests.integration.common.happy_path_test import SimUniqueProps


def test_happy_path():
    run_happy_path(
        SimUniqueProps(
            sim_type="bluesky",
            dt=0.05,
            initial_utc_datetime=datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            ),
        )
    )
