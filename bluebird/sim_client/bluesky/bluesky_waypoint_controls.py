"""
Contains the AbstractWaypointControls implementation for BlueSky
"""

# Note(RKM 2019-11-24) BlueSky's set of commands relating to waypoints isn't that great,
# so we just have to keep track of them ourselves (other then the DEFWPT command)

from typing import Optional, Union

import bluebird.utils.types as types
from bluebird.sim_client.bluesky.bluesky_client import BlueSkyClient
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls


class BlueSkyWaypointControls(AbstractWaypointControls):
    """
    AbstractWaypointControls implementation for BlueSky
    """

    @property
    def all_waypoints(self) -> Union[str, list]:
        return self._waypoints

    def __init__(self, bluesky_client: BlueSkyClient):
        self._bluesky_client = bluesky_client
        self._waypoints = set()

    def find(self, waypoint_name: str) -> Optional[types.Waypoint]:
        for wpt in self._waypoints:
            if wpt.name == waypoint_name:
                return wpt
