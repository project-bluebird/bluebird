"""
BlueBird metrics provider class
"""

import logging

import bluebird.settings as bb_settings
from bluebird.metrics.bluebird import metrics
from bluebird.metrics.metrics_provider import MetricProvider


class Provider(MetricProvider):
	"""
	BlueBird metrics provider
	"""

	def __init__(self, ac_data):
		super().__init__()
		self._logger = logging.getLogger(__package__)
		self._ac_data = ac_data

	def __call__(self, metric, *args, **kwargs):
		return getattr(metrics, metric)(self._ac_data, *args, **kwargs)

	def __str__(self):
		return 'BlueBirdProvider'

	def version(self):
		# Just track these metrics along with BlueBird release versions
		return str(bb_settings.VERSION)
