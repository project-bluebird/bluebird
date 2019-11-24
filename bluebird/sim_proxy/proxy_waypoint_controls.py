"""
Contains the ProxyWaypointControls class
"""

import random

from typing import Optional, Union, List
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls

import bluebird.utils.types as types


class ProxyWaypointControls(AbstractWaypointControls):
    """Proxy implementation of AbstractWaypointControls"""

    @property
    def all_waypoints(self) -> Union[str, list]:
        if not self.waypoints:
            waypoints = self._waypoint_controls.all_waypoints
            if not isinstance(waypoints, list):
                return waypoints
            self.waypoints = waypoints
        return self.waypoints

    def __init__(self, waypoint_controls: AbstractWaypointControls):
        self._waypoint_controls = waypoint_controls
        self.waypoints: List[types.Waypoint] = []

    def find(self, waypoint_name: str) -> Optional[types.Waypoint]:
        assert waypoint_name, "Must provide a waypoint_name"
        waypoint = self._find_by_name(waypoint_name)
        if not waypoint:
            # TODO(RKM 2019-11-19) We could fall-through and check if the sim_client can
            # find the waypoint #multi-client:
            # return self._waypoint_controls.find(waypoint_name)
            return None
        assert len(waypoint) == 1, f'Duplicate waypoints with name "{waypoint_name}"'
        return waypoint[0]

    def define(
        self, name: Optional[str], position: types.LatLon, **kwargs
    ) -> Union[types.Waypoint, str]:
        assert position, "Must provide a position"
        if not name:
            if [x for x in self.waypoints if x.position == position]:
                return f"A waypoint with LatLon {position} already exists"
            name = str(random.randint(100, 999))

        if self._find_by_name(name):
            return f'A waypoint named "{name}" already exists'

        res = self._waypoint_controls.define(name, position, **kwargs)
        if not isinstance(res, types.Waypoint):
            return res
        self.waypoints.append(res)
        return res

    def _find_by_name(self, name: str):
        return [x for x in self.waypoints if x.name == name]
