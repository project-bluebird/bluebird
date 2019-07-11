"""
BlueBird metrics provider class
"""

import logging

import bluebird.settings as bb_settings
from bluebird.metrics.metrics_provider import MetricProvider
from . import metrics


class Provider(MetricProvider):
	"""
	BlueBird metrics provider
	"""

	def __init__(self):
		super().__init__()
		self._logger = logging.getLogger(__package__)

	def __call__(self, metric, *args, **kwargs):
		return getattr(metrics, metric)(*args, **kwargs)

	def __str__(self):
		return 'BlueBirdProvider'

	def version(self):
		# Just track these metrics along with BlueBird release versions
		return str(bb_settings.VERSION)
