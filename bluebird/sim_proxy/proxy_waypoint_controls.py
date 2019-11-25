"""
Contains the ProxyWaypointControls class
"""

import random

from typing import Optional, Union, Set
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls

import bluebird.utils.types as types


class ProxyWaypointControls(AbstractWaypointControls):
    """
    Proxy implementation of AbstractWaypointControls

    Since the waypoint definitions shouldn't change (without us knowing), we can keep a
    simple cache of them here to avoid excess requests to the simulator
    """

    @property
    def all_waypoints(self) -> Union[str, list]:
        if not self._waypoints:
            waypoints = self._waypoint_controls.all_waypoints
            if not isinstance(waypoints, list):
                return waypoints
            self._waypoints = waypoints
        return self._waypoints

    def __init__(self, waypoint_controls: AbstractWaypointControls):
        self._waypoint_controls = waypoint_controls
        self._waypoints: Set[types.Waypoint] = set()

    def find(self, waypoint_name: str) -> Optional[types.Waypoint]:
        assert waypoint_name, "Must provide a waypoint_name"
        waypoint = self._find_by_name(waypoint_name)
        if not waypoint:
            # TODO(RKM 2019-11-19) We could fall-through and check if the sim_client can
            # find the waypoint #multi-client:
            # return self._waypoint_controls.find(waypoint_name)
            return None
        return waypoint[0]

    def define(
        self, name: Optional[str], position: types.LatLon, **kwargs
    ) -> Union[types.Waypoint, str]:
        assert position, "Must provide a position"
        if not name:
            if [x for x in self._waypoints if x.position == position]:
                return f"A waypoint with LatLon {position} already exists"
            name = str(random.randint(100, 999))

        if self._find_by_name(name):
            return f'A waypoint named "{name}" already exists'

        res = self._waypoint_controls.define(name, position, **kwargs)
        if not isinstance(res, types.Waypoint):
            return res
        self._waypoints.append(res)
        return res

    def _find_by_name(self, name: str) -> Optional[types.Waypoint]:
        for waypoint in self._waypoints:
            if waypoint.name == name:
                return waypoint
        return None
