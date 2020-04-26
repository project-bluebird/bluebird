"""
BlueBird metrics provider class
"""
import logging

from bluebird.metrics.abstract_metrics_provider import AbstractMetricsProvider
from bluebird.metrics.bluebird import metrics
from bluebird.settings import Settings


class Provider(AbstractMetricsProvider):
    """BlueBird metrics provider"""

    def __init__(self):
        self._logger = logging.getLogger(__name__)

    def __call__(self, metric, *args, **kwargs):
        # TODO (rkm 2020-01-12) Check _metric prefix
        return getattr(metrics, metric)(*args, **kwargs)

    def __str__(self):
        return "BlueBird"

    def version(self):
        # Just track these metrics along with BlueBird release versions
        return str(Settings.VERSION)
