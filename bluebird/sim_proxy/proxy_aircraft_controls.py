"""
Contains the ProxyAircraftControls class
"""

import logging

from typing import Optional, List, Union, Dict

import bluebird.utils.types as types
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls
from bluebird.utils.properties import AircraftProperties, AircraftRoute


class ProxyAircraftControls(AbstractAircraftControls):
    """Proxy implementation of AbstractAircraftControls"""

    @property
    def stream_data(self) -> List[AircraftProperties]:
        raise NotImplementedError

    @property
    def callsigns(self) -> Union[List[types.Callsign], str]:
        raise NotImplementedError

    # @property
    # def routes(self) -> Dict[types.Callsign, List]:
    #     raise NotImplementedError

    def __init__(self, aircraft_controls: AbstractAircraftControls):

        self._logger = logging.getLogger(__name__)

        self._aircraft_controls = aircraft_controls

        self._store: Dict[types.Callsign, AircraftProperties] = {}

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:
        raise NotImplementedError

    def set_heading(
        self, callsign: types.Callsign, heading: types.Heading
    ) -> Optional[str]:
        raise NotImplementedError

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        raise NotImplementedError

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        raise NotImplementedError

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: types.Waypoint
    ) -> Optional[str]:
        raise NotImplementedError

    def add_waypoint_to_route(
        self, callsign: types.Callsign, waypoint: types.Waypoint, **kwargs
    ) -> Optional[str]:
        raise NotImplementedError

    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
        speed: int,
    ) -> Optional[str]:
        raise NotImplementedError

    def get_properties(
        self, callsign: types.Callsign
    ) -> Union[AircraftProperties, str]:
        raise NotImplementedError

    def get_route(self, callsign: types.Callsign) -> Union[AircraftRoute, str]:
        raise NotImplementedError

    def exists(self, callsign: types.Callsign) -> Union[bool, str]:
        raise NotImplementedError

    def get_all_properties(
        self,
    ) -> Union[Dict[types.Callsign, AircraftProperties], str]:
        raise NotImplementedError
