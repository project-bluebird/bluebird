"""
Contains the ProxyWaypointControls class
"""

from typing import Optional, Union
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls

import bluebird.utils.types as types


class ProxyWaypointControls(AbstractWaypointControls):
    """Proxy implementation of AbstractWaypointControls"""

    @property
    def waypoints(self) -> Union[str, dict]:
        raise NotImplementedError

    def __init__(self, waypoint_controls: AbstractWaypointControls):
        self._waypoint_controls = waypoint_controls

    def find(self, waypoint_name: str) -> Optional[types.Waypoint]:
        raise NotImplementedError

    def define(
        self, name: Optional[str], position: types.LatLon, **kwargs
    ) -> Union[types.Waypoint, str]:
        raise NotImplementedError
