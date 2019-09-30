"""
Tests for BlueBird's built-in metrics
"""

# pylint: disable=redefined-outer-name

import numpy as np
import pytest

import bluebird.metrics.bluebird.config as cfg
from bluebird.cache import AcDataCache, SimState
from bluebird.metrics import setup_metrics
from bluebird.metrics.bluebird import Provider
from tests.unit import TEST_ACIDS, TEST_DATA


@pytest.fixture
def test_ac_data():
    """
    Yields a new AcDataCache instance for each test
    :return:
    """

    sim_state = SimState()
    ac_data = AcDataCache(sim_state)
    yield ac_data


@pytest.fixture
def test_bb_provider(test_ac_data):
    """
    Yields a new Provider instance for each test
    :param test_ac_data:
    :return:
    """

    yield Provider(test_ac_data)


def _other_cfg():
    """
    Second config available for testing
    :return:
    """

    cfg.VERT_LOS_SCORE = -10
    cfg.VERT_MIN_DIST = 5_000
    cfg.VERT_WARN_DIST = 45_000
    cfg.HOR_LOS_SCORE = -10
    cfg.HOR_MIN_DIST = 10
    cfg.HOR_WARN_DIST = 50


def test_metrics_setup(test_ac_data):
    """
    Tests that each provider can be imported and implements the MetricsProvider ABC fully
    :param test_ac_data:
    :return:
    """

    assert setup_metrics(test_ac_data), "Expected the providers to be loaded"


def test_invalid_inputs(test_bb_provider):
    """
    Tests calling the basic metrics with invalid inputs
    :param test_bb_provider:
    :return:
    """

    metrics = ["vertical_separation", "horizontal_separation"]

    for metric in metrics:
        with pytest.raises(TypeError):
            test_bb_provider(metric)
        with pytest.raises(AssertionError):
            test_bb_provider(metric, 123, 456)


@pytest.mark.parametrize("config_fn", [None, _other_cfg])
def test_vertical_separation_values(test_ac_data, test_bb_provider, config_fn):
    """
    Test the basic vertical separation endpoint
    :param test_ac_data:
    :param test_bb_provider:
    :param config_fn:
    :return:
    """

    metric = "vertical_separation"
    (ac1, ac2) = TEST_ACIDS

    if config_fn:
        config_fn()

    TEST_DATA["alt"][0] = 0
    TEST_DATA["alt"][1] = 0
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == cfg.VERT_LOS_SCORE
    ), "Expected the min score at 0 separation"

    TEST_DATA["alt"][1] = cfg.VERT_MIN_DIST
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == cfg.VERT_LOS_SCORE
    ), "Expected the min score at the min separation"

    TEST_DATA["alt"][1] = cfg.VERT_WARN_DIST
    test_ac_data.fill(TEST_DATA)
    assert test_bb_provider(metric, ac1, ac2) == 0, "Expected 0 at the warning dist"

    TEST_DATA["alt"][1] = cfg.VERT_WARN_DIST + 10_000
    test_ac_data.fill(TEST_DATA)
    assert test_bb_provider(metric, ac1, ac2) == 0, "Expected 0 beyond the warning dist"

    midpoint = cfg.VERT_WARN_DIST - cfg.VERT_MIN_DIST
    expected = np.interp(
        midpoint, [cfg.VERT_MIN_DIST, cfg.VERT_WARN_DIST], [cfg.VERT_LOS_SCORE, 0]
    )

    TEST_DATA["alt"][1] = midpoint
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == expected
    ), "Expected linear score between the min and warning"


@pytest.mark.parametrize("config_fn", [None, _other_cfg])
def test_horizontal_separation_values(test_ac_data, test_bb_provider, config_fn):
    """
    Test the basic horizontal separation endpoint
    :param test_ac_data:
    :param test_bb_provider:
    :param config_fn:
    :return:
    """

    metric = "horizontal_separation"
    (ac1, ac2) = TEST_ACIDS

    if config_fn:
        config_fn()

    # NOTE: 1 degree of latitude is always 60 nautical miles, so we can test the separation
    # calculation by just varying the latitude of the test aircraft

    TEST_DATA["lat"][0] = 0
    TEST_DATA["lat"][1] = 0
    TEST_DATA["lon"][0] = 0
    TEST_DATA["lon"][1] = 0
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == cfg.HOR_LOS_SCORE
    ), "Expected the min score at 0 separation"

    TEST_DATA["lat"][1] = cfg.HOR_MIN_DIST / 60
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == cfg.HOR_LOS_SCORE
    ), "Expected the min score at the min separation"

    TEST_DATA["lat"][1] = (
        cfg.HOR_MIN_DIST + 0.5 * (cfg.HOR_WARN_DIST - cfg.HOR_MIN_DIST)
    ) / 60
    test_ac_data.fill(TEST_DATA)
    expected = 0.5 * cfg.HOR_LOS_SCORE
    assert (
        test_bb_provider(metric, ac1, ac2) == expected
    ), "Expected linear score between the min and warning dist"

    TEST_DATA["lat"][1] = cfg.HOR_WARN_DIST / 60
    test_ac_data.fill(TEST_DATA)
    assert test_bb_provider(metric, ac1, ac2) == 0, "Expected 0 at the warning dist"

    TEST_DATA["lat"][1] = (10 + cfg.HOR_WARN_DIST) / 60
    test_ac_data.fill(TEST_DATA)
    assert test_bb_provider(metric, ac1, ac2) == 0, "Expected 0 beyond the warning dist"
