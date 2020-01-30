"""
Contains the ProxyAircraftControls class
"""
import copy
import logging
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Union

from aviary.sector.route import Route
from aviary.sector.sector_element import SectorElement

import bluebird.utils.types as types
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls
from bluebird.utils.properties import AircraftProperties


class ProxyAircraftControls(AbstractAircraftControls):
    """Proxy implementation of AbstractAircraftControls"""

    @property
    def all_properties(self) -> Union[Dict[types.Callsign, AircraftProperties], str]:
        self._logger.debug("all_properties: Accessed")
        if self._data_valid:
            self._logger.debug("all_properties: Using cache")
            return self._ac_props
        all_props = self._aircraft_controls.all_properties
        if not isinstance(all_props, dict):
            return all_props
        for callsign in list(self._ac_props):
            if callsign not in all_props:
                self._logger.warning(
                    f"all_properties: Aircraft {callsign} has "
                    "been removed from the simulation"
                )
                self._ac_props.pop(callsign, None)
                continue
            self._update_ac_properties(callsign, all_props[callsign])
        self._logger.debug("all_properties: Data now valid")
        self._data_valid = True
        return self._ac_props

    @property
    def callsigns(self) -> Union[List[types.Callsign], str]:
        if not self._data_valid:
            err = self.all_properties
            if isinstance(err, str):
                return err
        return list(self._ac_props.keys())

    def __init__(self, aircraft_controls: AbstractAircraftControls):
        self._logger = logging.getLogger(__name__)
        self._aircraft_controls = aircraft_controls

        self._ac_props: Dict[types.Callsign, Optional[AircraftProperties]] = {}
        self._prev_ac_props: Dict[types.Callsign, Optional[AircraftProperties]] = {}
        self._routes: Dict[str, Route] = {}
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
    ) -> Optional[str]:
        return self._aircraft_controls.set_ground_speed(callsign, ground_speed)

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ) -> Optional[str]:
        return self._aircraft_controls.set_vertical_speed(callsign, vertical_speed)

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: str
    ) -> Optional[str]:
        props = self.properties(callsign)
        if not isinstance(props, AircraftProperties):
            return props
        if not props.route_name:
            return "Aircraft has no route"
        route_waypoints = [x[0] for x in self._routes[props.route_name].fix_list]
        if waypoint not in route_waypoints:
            return f'Waypoint "{waypoint}" is not in the route {route_waypoints}'
        return self._aircraft_controls.direct_to_waypoint(callsign, waypoint)

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
        exists = self.exists(callsign)
        if not isinstance(exists, bool):
            return exists
        if self.exists(callsign):
            return "Aircraft already exists"
        err = self._aircraft_controls.create(
            callsign, ac_type, position, heading, altitude, gspd
        )
        if err:
            return err
        # Create an empty entry for the new aircraft and ensure we get new data back
        self._ac_props[callsign] = None
        self._data_valid = False
        all_properties = self.all_properties
        if not isinstance(all_properties, dict):
            return all_properties
        return (
            None if callsign in all_properties else "New callsign missing from sim data"
        )

    def exists(self, callsign: types.Callsign) -> Union[bool, str]:
        all_callsings = self.callsigns
        return (
            bool(callsign in all_callsings)
            if isinstance(all_callsings, list)
            else all_callsings
        )

    def properties(self, callsign: types.Callsign) -> Union[AircraftProperties, str]:
        """Utility function to return only the properties for the specified aircraft"""
        all_props = self.all_properties
        if not isinstance(all_props, dict):
            return all_props
        return all_props.get(callsign, None) or f"Unknown callsign {callsign}"

    def route(self, callsign: types.Callsign) -> Union[Tuple[str, str, List[str]], str]:
        """Utility function to return only the route for the specified aircraft"""
        props = self.properties(callsign)
        if not isinstance(props, AircraftProperties):
            return props
        if not props.route_name:
            return "Aircraft has no route"

        route = self._routes[props.route_name]
        next_waypoint = route.next_waypoint(
            props.position.lat_degrees, props.position.lon_degrees
        )
        return (props.route_name, next_waypoint, [x[0] for x in route.fix_list])

    def invalidate_data(self, clear: bool = False) -> None:
        """Clears the data_valid flag"""
        if clear:
            self._ac_props = {}
            self._prev_ac_props = {}
        self._data_valid = False

    def store_current_props(self):
        # TODO(rkm 2020-01-12) In sandbox mode, this needs to be hooked-up to a timer
        # which stores the current state every n seconds
        self.prev_step_props = copy.deepcopy(self._ac_props)

    def prev_ac_props(self) -> Dict[types.Callsign, Optional[AircraftProperties]]:
        # NOTE(rkm 2020-01-29) Defensive copy
        return copy.deepcopy(self._prev_ac_props)

    def set_initial_properties(
        self, sector_element: SectorElement, scenario_content: dict
    ) -> None:
        """
        Set any properties which are not tracked by the simulator - i.e. the flight
        levels, routes, and aircraft types
        """

        for route in sector_element.routes():
            self._routes[route.name] = route

        new_props: Dict[types.Callsign, AircraftProperties] = {}
        for aircraft in scenario_content["aircraft"]:
            callsign = types.Callsign(aircraft["callsign"])
            new_props[callsign] = AircraftProperties.from_data(aircraft)
            if "route" not in aircraft:
                new_props[callsign].route_name = None
                continue
            # Match the route name to the waypoints in the scenario data
            aircraft_route_waypoints = [x["fixName"] for x in aircraft["route"]]
            new_props[callsign].route_name = next(
                x
                for x in self._routes
                if self._routes[x].fix_names() == aircraft_route_waypoints
            )

        self._ac_props = new_props
        self._data_valid = False

    def _update_ac_properties(
        self, callsign: types.Callsign, new_props: AircraftProperties
    ):
        """Updates the stored AircraftProperties with new data from the simulator"""
        # NOTE(rkm 2020-01-12) If we don't have any existing properties, then that means
        # this is an aircraft that has been created after the scenario has been started.
        # We therefore (currently) don't have any route or req. flight level information
        if not self._ac_props[callsign]:
            self._ac_props[callsign] = new_props
        else:
            props = self._ac_props[callsign]
            props.altitude = new_props.altitude
            props.ground_speed = new_props.ground_speed
            props.heading = new_props.heading
            props.position = new_props.position
            props.vertical_speed = new_props.vertical_speed
