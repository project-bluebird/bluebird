"""
Contains the ProxyAircraftControls class
"""

import copy
import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import bluebird.utils.types as types
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls
from bluebird.utils.properties import AircraftProperties
from bluebird.utils.properties import AircraftRoute


class ProxyAircraftControls(AbstractAircraftControls):
    """Proxy implementation of AbstractAircraftControls"""

    @property
    def all_properties(self,) -> Union[Dict[types.Callsign, AircraftProperties], str]:

        if not self._ac_props:
            err = self._set_initial_properties()
            if err:
                return err

        if not self._data_valid:
            all_props = self._aircraft_controls.all_properties
            if not isinstance(all_props, dict):
                return all_props
            for callsign in list(self._ac_props):
                if callsign not in all_props:
                    # Aircraft has been removed from the simulation
                    self._ac_props.pop(callsign, None)
                self._update_ac_properties(callsign, all_props[callsign])
            self._data_valid = True

        return self._ac_props

    @property
    def callsigns(self) -> Union[List[types.Callsign], str]:
        props = self.all_properties
        if isinstance(props, str):
            return props
        return list(self._ac_props.keys())

    @property
    def all_routes(self) -> Union[Dict[types.Callsign, AircraftRoute], str]:
        props = self.all_properties
        if isinstance(props, str):
            return props
        return [{ac.callsign: ac.route} for ac in props]

    def __init__(self, aircraft_controls: AbstractAircraftControls):
        self._logger = logging.getLogger(__name__)
        self._aircraft_controls = aircraft_controls

        self._ac_props: Dict[types.Callsign, Optional[AircraftProperties]] = {}
        self._prev_ac_props: Dict[types.Callsign, Optional[AircraftProperties]] = {}
        self._data_valid: bool = False

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:
        err = self._aircraft_controls.set_cleared_fl(callsign, flight_level, **kwargs)
        if err:
            return err
        self._ac_props[callsign].cleared_flight_level = flight_level
        return None

    def set_heading(
        self, callsign: types.Callsign, heading: types.Heading
    ) -> Optional[str]:
        return self._aircraft_controls.set_heading(callsign, heading)

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        return self._aircraft_controls.set_ground_speed(callsign, ground_speed)

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        return self._aircraft_controls.set_vertical_speed(callsign, vertical_speed)

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: types.Waypoint
    ) -> Optional[str]:
        if not self.exists(callsign):
            return f"Unrecognised callsign {callsign}"
        return "Err"
        # TODO(rkm 2020-01-12) Needs to be able to check the sector waypoints
        # route_waypoints = [x.waypoint for x in self._ac_routes[callsign].segments]
        # if waypoint not in route_waypoints:
        #     return "Waypoint not on the route"
        # err = self._aircraft_controls.direct_to_waypoint(callsign, waypoint)
        # if err:
        #     return err
        # return None

    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
        gspd: types.GroundSpeed,
    ) -> Optional[str]:
        # NOTE(RKM 2019-11-20) Creating an aircraft with a specified route is currently
        # not implemented
        if self.exists(callsign):
            return "Aircraft already exists"
        err = self._aircraft_controls.create(
            callsign, ac_type, position, heading, altitude, gspd
        )
        if err:
            return err
        # Create an empty entry for the new aircraft
        self._ac_props[callsign] = None
        return None

    def exists(self, callsign: types.Callsign) -> Union[bool, str]:
        all_callsings = self.callsigns
        return (
            bool(callsign in all_callsings)
            if isinstance(all_callsings, list)
            else all_callsings
        )

    def properties(self, callsign: types.Callsign) -> Union[AircraftProperties, str]:
        """Utility function to return only the properties for the specified aircraft"""
        if not self.exists(callsign):
            return f"Unrecognised callsign {callsign}"
        if not self._ac_props[callsign].is_valid:
            self._update_ac_props(callsign)
        return self._ac_props[callsign]

    def route(self, callsign: types.Callsign) -> Optional[Union[AircraftRoute, str]]:
        """Utility function to return only the route for the specified aircraft"""
        props = self.properties(callsign)
        if not isinstance(props, AircraftProperties):
            return props
        return props.route or "Aircraft has no route"

    def invalidate_data(self):
        """Clears the data_valid flag"""
        self._data_valid = False

    def store_current_props(self):
        # TODO(rkm 2020-01-12) In sandbox mode, this needs to be hooked-up to a timer
        # which stores the current state every n seconds
        self.prev_step_props = copy.deepcopy(self._ac_props)

    def prev_ac_props(self):
        return self._prev_ac_props

    def _set_initial_properties(self) -> Optional[str]:
        """
        Set and properties which are not tracked by the simulator - i.e. the flight
        levels, routes, and aircraft types
        """
        all_props = self._aircraft_controls.all_properties
        if not isinstance(all_props, dict):
            return all_props
        for callsign, data in all_props.items():
            self._ac_props[callsign] = AircraftProperties()

        self._data_valid = True
        return self._ac_props

    def _update_ac_properties(
        self, callsign: types.Callsign, new_props: AircraftProperties
    ):
        """Update the variable bits for props which already exist in the store"""
        # NOTE(rkm 2020-01-12) If we don't have any existing properties, then that means
        # this is an aircraft that has been created after the scenario has been started.
        # We therefore (currently) don't have any route or req. flight level information
        if not self._ac_props[callsign]:
            self._ac_props[callsign] = new_props
        else:
            props = self._ac_props[callsign]
            props.altitude: types = new_props.altitude
            props.ground_speed: types = new_props.ground_speed
            props.heading: types = new_props.heading
            props.position: types = new_props.position
            props.vertical_speed: types = new_props.vertical_speed
