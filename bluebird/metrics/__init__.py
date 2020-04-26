"""
Package contains BlueBird's metrics code
"""
import importlib.util
import logging
from typing import List

from bluebird.metrics.abstract_metrics_provider import AbstractMetricsProvider
from bluebird.settings import Settings
from bluebird.utils.properties import SimType

_LOGGER = logging.getLogger(__name__)

METRICS_PROVIDERS: List[str] = ["bluebird"]


class MetricsProviders:
    """Utility class to wrap the available metrics providers"""

    def __init__(self, providers: List[AbstractMetricsProvider]):
        self.providers = providers

    def get(self, name: str) -> AbstractMetricsProvider:
        return next((x for x in self.providers if str(x).lower() == name.lower()), None)

    def __iter__(self):
        yield from self.providers

    def __bool__(self):
        return bool(self.providers)


def setup_metrics() -> List[AbstractMetricsProvider]:
    """
    Loads the metrics providers defined in the global settings. Returns them as a list
    """

    if Settings.SIM_TYPE == SimType.MachColl:
        METRICS_PROVIDERS.append("machcoll")

    providers = []
    for provider in METRICS_PROVIDERS:
        mod_path = f"{__package__}.{provider}.provider"
        try:
            spec = importlib.util.find_spec(mod_path)
            if spec is None:
                raise ModuleNotFoundError(f"Can't find {mod_path}")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            providers.append(getattr(module, "Provider")())
        except ModuleNotFoundError as exc:
            _LOGGER.error(f"Couldn't import {mod_path}. Check the module exists")
            raise exc

    return MetricsProviders(providers)
