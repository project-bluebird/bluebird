"""
MachColl metrics provider class
"""
import logging
from pathlib import Path
from typing import Dict
from typing import Optional
from typing import Union

from semver import VersionInfo

from bluebird.metrics.abstract_metrics_provider import AbstractMetricsProvider

# NOTE(RKM 2019-11-26) The names of the available metrics are currently defined in this
# file. This has to be imported/created to make the MachColl metrics available since it
# is not included in the repo
_METRICS_FILE = Path("bluebird", "metrics", "machcoll", "metrics_list.txt")


class Provider(AbstractMetricsProvider):
    """MachColl metrics provider"""

    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._version: VersionInfo = None
        self.metrics: Dict[str, float] = {}
        self._load_metrics_from_file()

    def __call__(self, metric, *args, **kwargs):
        if metric not in self.metrics:
            raise AttributeError(f"No metric named '{metric}'")
        res = self.metrics[metric]
        return res if res else f"Metric '{metric}' has no value set"

    def __str__(self):
        return "MachColl"

    def version(self):
        return str(self._version)

    def set_version(self, version: VersionInfo):
        """Allows the version to be set after connection to the simulation server"""
        self._version = version

    def _load_metrics_from_file(self):
        if not _METRICS_FILE.exists():
            self._logger.error(
                "Couldn't find metrics list, no metrics will be available"
            )
            return None
        with open(_METRICS_FILE) as f:
            lines = f.readlines()
        for line in [x for x in lines if x.rstrip("\n")]:
            self.metrics[line.rstrip()] = None
        self._logger.debug(f"Loaded metrics: {', '.join(self.metrics.keys())}")

    def update(self, metric: str, result: Optional[Union[str, float]]):
        if not isinstance(result, (float, int)):
            self._logger.error(f"Metric {metric} returned result {result}")
            self.metrics[metric] = str(result)
            return
        self.metrics[metric] = result
