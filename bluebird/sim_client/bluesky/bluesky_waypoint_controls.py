"""
Contains the AbstractWaypointControls implementation for BlueSky
"""

from typing import Optional, Union

import bluebird.utils.types as types
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls


class BlueSkyWaypointControls(AbstractWaypointControls):
    """
    AbstractWaypointControls implementation for BlueSky
    """

    @property
    def all_waypoints(self) -> Union[str, list]:
        raise NotImplementedError

    def __init__(self, sim_client):
        self._sim_client = sim_client

    def find(self, waypoint_name: str) -> Optional[types.Waypoint]:
        raise NotImplementedError

    def define(
        self, name: Optional[str], position: types.LatLon, **kwargs
    ) -> Union[types.Waypoint, str]:
        raise NotImplementedError
