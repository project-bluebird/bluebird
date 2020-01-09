"""
Contains the ProxyWaypointControls class
"""

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
        return waypoint

    def _find_by_name(self, name: str) -> Optional[types.Waypoint]:
        for waypoint in self._waypoints:
            if waypoint.name == name:
                return waypoint
        return None
