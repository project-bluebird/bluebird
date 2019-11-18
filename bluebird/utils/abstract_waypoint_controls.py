"""
Contains the AbstractWaypointControls class
"""

from abc import ABC, abstractmethod
from typing import Optional, Union

import bluebird.utils.types as types


class AbstractWaypointControls(ABC):
    """
    Abstract class defining waypoint control functions
    """

    # TODO Will need a mapping between each client format and BlueBird's implementation
    # TODO(RKM 2019-11-18) This can probably be cached once since we will be the ones
    # updating any waypoints
    @property
    @abstractmethod
    def waypoints(self) -> Union[str, dict]:
        """
        Get all the waypoints (fixes) defined in the simulation, or a string to indicate
        any error
        """

    @abstractmethod
    def find(self, waypoint_name: str) -> Optional[types.Waypoint]:
        """
        Returns the waypoint for the given name if it exists, otherwise None
        :param waypoint_name:
        """

    @abstractmethod
    def define(
        self, name: Optional[str], position: types.LatLon, **kwargs
    ) -> Union[types.Waypoint, str]:
        """
        Defines a waypoint and returns the Waypoint object
        :param name: If not set, a name will automatically be generated
        """
