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

    # @property
    # def stream_data(self) -> Optional[List[AircraftProperties]]:
    #     raise NotImplementedError

    @property
    def all_properties(self) -> Union[Dict[types.Callsign, AircraftProperties], str]:
        if not self.ac_props:
            all_props = self._aircraft_controls.all_properties
            if not isinstance(all_props, dict):
                return all_props
            self.ac_props = all_props
        # Update any properties which have been invalidated
        for callsign in [k for k, v in self.ac_props.items() if not v]:
            new_ac_props = self.properties(callsign)
            if isinstance(new_ac_props, AircraftProperties):  # New props
                self.ac_props[callsign] = new_ac_props
            elif not new_ac_props:  # No props - aircraft has been removed
                del self.ac_props[callsign]
            else:  # Error
                return new_ac_props
        # NOTE(RKM 2019-11-20) Pyright complains here about the dict values being marked
        # Optional, however we check for this above
        return self.ac_props  # type: ignore

    @property
    def callsigns(self) -> Union[List[types.Callsign], str]:
        err = self.all_properties
        if isinstance(err, str):
            return err
        return list(self.ac_props.keys())

    # @property
    # def routes(self) -> Dict[types.Callsign, List]:
    #     raise NotImplementedError

    def __init__(self, aircraft_controls: AbstractAircraftControls):
        self._aircraft_controls = aircraft_controls
        self._logger = logging.getLogger(__name__)
        self.ac_props: Dict[types.Callsign, Optional[AircraftProperties]] = {}
        self.ac_routes: Dict[types.Callsign, Optional[AircraftRoute]] = {}

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:
        assert callsign, "Must provide a valid callsign"
        assert flight_level, "Must provide a valid flight level"
        err = self._aircraft_controls.set_cleared_fl(callsign, flight_level, **kwargs)
        if err:
            return err
        self.ac_props[callsign] = None
        return None

    def set_heading(
        self, callsign: types.Callsign, heading: types.Heading
    ) -> Optional[str]:
        assert callsign, "Must provide a valid callsign"
        assert heading, "Must provide a valid heading"
        return self._checked_response(
            callsign, self._aircraft_controls.set_heading(callsign, heading)
        )

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        assert callsign, "Must provide a valid callsign"
        assert ground_speed, "Must provide a valid ground speed"
        return self._checked_response(
            callsign, self._aircraft_controls.set_ground_speed(callsign, ground_speed)
        )

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        assert callsign, "Must provide a valid callsign"
        assert vertical_speed, "Must provide a valid vertical speed"
        return self._checked_response(
            callsign,
            self._aircraft_controls.set_vertical_speed(callsign, vertical_speed),
        )

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

    def properties(
        self, callsign: types.Callsign
    ) -> Optional[Union[AircraftProperties, str]]:
        raise NotImplementedError

    def route(self, callsign: types.Callsign) -> Union[AircraftRoute, str]:
        raise NotImplementedError

    def exists(self, callsign: types.Callsign) -> Union[bool, str]:
        raise NotImplementedError

    def clear_caches(self):
        """Clears the caches"""
        self.ac_props = {}
        self.ac_routes = {}

    def _checked_response(
        self, callsign: types.Callsign, err: Optional[str]
    ) -> Optional[str]:
        if err:
            return err
        self.ac_props[callsign] = None
        return None
