"""
Contains the AbstractWaypointControls implementation for MachColl
"""

import logging
from typing import Optional, Union

import bluebird.utils.types as types
from bluebird.sim_client.machcoll.machcoll_client_imports import MCClientMetrics
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls


class MachCollWaypointControls(AbstractWaypointControls):
    """
    AbstractWaypointControls implementation for MachColl
    """

    def __init__(self, sim_client):
        self._sim_client = sim_client
        self._logger = logging.getLogger(__name__)

    @property
    def all_waypoints(self) -> Union[str, list]:
        fixes = self._mc_client().get_all_fixes()
        if not isinstance(fixes, dict):
            raise NotImplementedError(f"get_all_fixes returned: {fixes}")
        # TODO Need to create a mapping
        self._logger.warning(f"Unhandled data: {fixes}")
        return []

    def find(self, waypoint_name: str) -> Optional[types.Waypoint]:
        raise NotImplementedError

    def _mc_client(self) -> MCClientMetrics:
        return self._sim_client.mc_client
