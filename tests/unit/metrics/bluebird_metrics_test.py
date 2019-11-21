"""
Tests for BlueBird's built-in metrics
"""


import pytest

from bluebird.metrics import setup_metrics
import bluebird.metrics.bluebird.config as cfg
from bluebird.metrics.bluebird import Provider
from tests.unit import TEST_ACIDS, TEST_DATA


@pytest.fixture
def test_bb_provider(test_ac_data):
    """
    Yields a new Provider instance for each test
    :param test_ac_data:
    :return:
    """

    yield Provider(None)


def _other_cfg():
    """
    Second config available for testing
    :return:
    """

    cfg.LOS_SCORE = -10
    cfg.VERT_WARN_DIST = 45_000
    cfg.HOR_WARN_DIST = 50


def test_metrics_setup(test_ac_data):
    """
    Tests that each provider can be imported and implements the MetricsProvider ABC
    :param test_ac_data:
    :return:
    """

    assert setup_metrics(test_ac_data), "Expected the providers to be loaded"


def test_invalid_inputs(test_bb_provider):
    """
    Tests calling the basic metrics with invalid inputs
    :param bb_provider:
    :return:
    """

    metrics = ["aircraft_separation"]

    for metric in metrics:
        with pytest.raises(TypeError):
            test_bb_provider(metric)
        with pytest.raises(AssertionError):
            test_bb_provider(metric, 123, 456)


@pytest.mark.parametrize("config_fn", [None, _other_cfg])
def test_aircraft_separation_values(test_ac_data, test_bb_provider, config_fn):
    """
    Test the basic aircraft separation endpoint
    :param test_ac_data:
    :param test_bb_provider:
    :param config_fn:
    :return:
    """

    metric = "aircraft_separation"
    (ac1, ac2) = TEST_ACIDS

    if config_fn:
        config_fn()

    # Initial values
    TEST_DATA["lat"] = [0, 0]
    TEST_DATA["lon"] = [0, 0]
    TEST_DATA["alt"] = [0, 0]

    # Testing m(d_h, d_v) = 0, if d_h >= C_h (for any d_v)

    TEST_DATA["lat"][0] = 5  # Much greater than the minimum
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == 0
    ), "Expected 0 for large horizontal separation"

    TEST_DATA["alt"][1] = 5000
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == 0
    ), "Expected 0 for large horizontal separation"

    # Testing m(d_h, d_v) = 0, if d_v >= C_v (for any d_h)

    TEST_DATA["lat"][0] = 0
    TEST_DATA["alt"][1] = 50_000  # Much greater than the minimum
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == 0
    ), "Expected 0 for large vertical separation"

    TEST_DATA["lat"][0] = 5
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == 0
    ), "Expected 0 for large vertical separation"

    # Testing m(d_h, d_v) = -1, if d_h < c_h and d_v < c_v (loss of separation)

    TEST_DATA["lat"] = [0, 0]
    TEST_DATA["alt"] = [0, 0]
    test_ac_data.fill(TEST_DATA)
    assert (
        test_bb_provider(metric, ac1, ac2) == cfg.LOS_SCORE
    ), "Expected minimum score for LOS condition"


# TODO Plot metrics
