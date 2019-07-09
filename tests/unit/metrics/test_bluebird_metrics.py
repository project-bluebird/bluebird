"""
Tests for BlueBird's built-in metrics
"""

# pylint: disable=redefined-outer-name

import numpy as np
import pytest

import bluebird.cache as bb_cache
import bluebird.metrics as bb_metrics
import bluebird.metrics.bluebird.config as cfg
from bluebird.metrics.bluebird import Provider
from tests.unit import TEST_ACIDS, TEST_DATA


@pytest.fixture
def bb_provider():
	"""
	Yields a new Provider instance for each test
	:return:
	"""

	yield Provider()


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


def test_metrics_setup():
	"""
	Tests that each provider can be imported and implements the MetricsProvider ABC fully
	:return:
	"""

	bb_metrics.setup_metrics()
	assert bb_metrics.METRIC_PROVIDERS, 'Expected the providers to be loaded'


def test_invalid_inputs(bb_provider):
	"""
	Tests calling the basic metrics with invalid inputs
	:param bb_provider:
	:return:
	"""

	metrics = ['vertical_separation', 'horizontal_separation']

	for metric in metrics:
		with pytest.raises(TypeError):
			bb_provider(metric)
		with pytest.raises(AssertionError):
			bb_provider(metric, 123, 456)


@pytest.mark.parametrize('config_fn', [None, _other_cfg])
def test_vertical_separation_values(bb_provider, config_fn):
	"""
	Test the basic vertical separation endpoint
	:param bb_provider:
	:param config_fn:
	:return:
	"""

	metric = 'vertical_separation'
	(A1, A2) = TEST_ACIDS

	if config_fn:
		config_fn()

	TEST_DATA['alt'][0] = 0
	TEST_DATA['alt'][1] = 0
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == cfg.VERT_LOS_SCORE, \
		'Expected the min score at 0 separation'

	TEST_DATA['alt'][1] = cfg.VERT_MIN_DIST
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == cfg.VERT_LOS_SCORE, \
		'Expected the min score at the min separation'

	TEST_DATA['alt'][1] = cfg.VERT_WARN_DIST
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == 0, 'Expected 0 at the warning dist'

	TEST_DATA['alt'][1] = cfg.VERT_WARN_DIST + 10_000
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == 0, 'Expected 0 beyond the warning dist'

	midpoint = cfg.VERT_WARN_DIST - cfg.VERT_MIN_DIST
	expected = np.interp(midpoint, [cfg.VERT_MIN_DIST, cfg.VERT_WARN_DIST], [cfg.VERT_LOS_SCORE, 0])

	TEST_DATA['alt'][1] = midpoint
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == expected, \
		'Expected linear score between the min and warning'


@pytest.mark.parametrize('config_fn', [None, _other_cfg])
def test_horizontal_separation_values(bb_provider, config_fn):
	"""
	Test the basic horizontal separation endpoint
	:param bb_provider:
	:param config_fn:
	:return:
	"""

	metric = 'horizontal_separation'
	(A1, A2) = TEST_ACIDS

	if config_fn:
		config_fn()

	# NOTE: 1 degree of latitude is always 60 nautical miles, so we can test the separation
	# calculation by just varying the latitude of the test aircraft

	TEST_DATA['lat'][0] = 0
	TEST_DATA['lat'][1] = 0
	TEST_DATA['lon'][0] = 0
	TEST_DATA['lon'][1] = 0
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == cfg.HOR_LOS_SCORE, 'Expected the min score at 0 separation'

	TEST_DATA['lat'][1] = cfg.HOR_MIN_DIST / 60
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == cfg.HOR_LOS_SCORE, \
		'Expected the min score at the min separation'

	TEST_DATA['lat'][1] = (cfg.HOR_MIN_DIST + 0.5 * (cfg.HOR_WARN_DIST - cfg.HOR_MIN_DIST)) / 60
	bb_cache.AC_DATA.fill(TEST_DATA)
	expected = 0.5 * cfg.HOR_LOS_SCORE
	assert bb_provider(metric, A1, A2) == expected, \
		'Expected linear score between the min and warning dist'

	TEST_DATA['lat'][1] = cfg.HOR_WARN_DIST / 60
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == 0, 'Expected 0 at the warning dist'

	TEST_DATA['lat'][1] = (10 + cfg.HOR_WARN_DIST) / 60
	bb_cache.AC_DATA.fill(TEST_DATA)
	assert bb_provider(metric, A1, A2) == 0, 'Expected 0 beyond the warning dist'
