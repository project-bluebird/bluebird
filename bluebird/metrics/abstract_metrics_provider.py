"""
Contains the AbstractMetricsProvider abstract base class
"""
from abc import ABC
from abc import abstractmethod

from semver import VersionInfo


class AbstractMetricsProvider(ABC):
    """
    ABC for classes which provide metrics to BlueBird
    """

    @abstractmethod
    def __call__(self, metric, *args, **kwargs):
        pass

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def version(self) -> VersionInfo:
        """
        Return the version of the metrics module
        :return:
        """
