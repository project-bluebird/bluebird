"""
Contains the ProxyAircraftControls class
"""

# TODO(RKM 2019-11-21) Need to handle setting rfl and cfl, as the sim clients won't do
# this for us

# TODO(RKM 2019-11-21) There may be some edge-cases where an aircraft exists in ac_props
# but not in ac_routes. We should refactor this to ensure this is always the case, and
# add appropriate tests

import copy
import logging
from typing import Optional, List, Union, Dict

import bluebird.utils.properties as props
import bluebird.utils.types as types
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls


class ProxyAircraftControls(AbstractAircraftControls):
    """Proxy implementation of AbstractAircraftControls"""

    @property
    def all_properties(
        self,
    ) -> Union[Dict[types.Callsign, props.AircraftProperties], str]:
        if not self.ac_props:
            all_props = self._aircraft_controls.all_properties
            if not isinstance(all_props, dict):
                return all_props
            self._set_flight_levels(all_props)
            self.ac_props = all_props
        else:  # Update any properties which have been invalidated
            for callsign in [k for k, v in self.ac_props.items() if not v]:
                new_ac_props = self.properties(callsign)
                if isinstance(new_ac_props, props.AircraftProperties):  # New props
                    self.ac_props[callsign] = new_ac_props
                elif not new_ac_props:  # No props - aircraft has been removed
                    self.ac_props.pop(callsign, None)
                    self.ac_routes.pop(callsign, None)
                else:  # Error string
                    return new_ac_props
        return self.ac_props

    @property
    def callsigns(self) -> Union[List[types.Callsign], str]:
        err = self.all_properties
        if isinstance(err, str):
            return err
        return list(self.ac_props.keys())

    @property
    def all_routes(self) -> Union[Dict[types.Callsign, props.AircraftRoute], str]:
        if not self.ac_routes:
            ac_routes = self._aircraft_controls.all_routes
            if not isinstance(ac_routes, dict):
                return ac_routes
            self.ac_routes = ac_routes
        else:
            for callsign in [
                k for k, v in self.ac_routes.items() if v.current_segment_index is None
            ]:
                new_route = self.route(callsign)
                if isinstance(new_route, props.AircraftRoute):
                    self.ac_routes[callsign] = new_route
                elif not new_route:
                    self.ac_routes.pop(callsign, None)
        return self.ac_routes

    def __init__(self, aircraft_controls: AbstractAircraftControls):
        self._aircraft_controls = aircraft_controls
        self._logger = logging.getLogger(__name__)
        # TODO(RKM 2019-11-21) Make private and refactor tests
        self.ac_props: Dict[types.Callsign, Optional[props.AircraftProperties]] = {}
        self.ac_routes: Dict[types.Callsign, props.AircraftRoute] = {}

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:
        self._assert_valid_args([callsign, flight_level])
        err = self._aircraft_controls.set_cleared_fl(callsign, flight_level, **kwargs)
        if err:
            return err
        self.ac_props[callsign] = None
        return None

    def set_heading(
        self, callsign: types.Callsign, heading: types.Heading
    ) -> Optional[str]:
        self._assert_valid_args([callsign, heading])
        return self._checked_response(
            callsign, self._aircraft_controls.set_heading(callsign, heading)
        )

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        self._assert_valid_args([callsign, ground_speed])
        return self._checked_response(
            callsign, self._aircraft_controls.set_ground_speed(callsign, ground_speed)
        )

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        self._assert_valid_args([callsign, vertical_speed])
        return self._checked_response(
            callsign,
            self._aircraft_controls.set_vertical_speed(callsign, vertical_speed),
        )

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: types.Waypoint
    ) -> Optional[str]:
        self._assert_valid_args([callsign, waypoint])
        assert callsign in self.ac_props, "Callsign not in aircraft data"
        route_waypoints = [x.waypoint for x in self.ac_routes[callsign].segments]
        if waypoint not in route_waypoints:
            return "Waypoint not on the route"
        err = self._aircraft_controls.direct_to_waypoint(callsign, waypoint)
        if err:
            return err
        return None

    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
        gspd: types.GroundSpeed,
    ) -> Optional[str]:
        self._assert_valid_args([callsign, ac_type, position, heading, altitude, gspd])
        assert callsign not in self.ac_props, "Aircraft already exists"
        err = self._aircraft_controls.create(
            callsign, ac_type, position, heading, altitude, gspd
        )
        if err:
            return err
        print(f"Calling props with {callsign}")
        ac_props = self.properties(callsign)
        assert isinstance(
            ac_props, props.AircraftProperties
        ), "Couldn't get properties for newly created aircraft"
        # NOTE(RKM 2019-11-21) Don't need to back-fill the cache here since the call to
        # properties will do that
        # NOTE(RKM 2019-11-20) Creating an aircraft with a specified route is currently
        # not implemented. This can be achieved by now by performing multiple ADDWPT
        # commands after the aircraft is created though
        self.ac_routes[callsign] = props.AircraftRoute(callsign, [], None)
        return None

    def properties(
        self, callsign: types.Callsign
    ) -> Optional[Union[props.AircraftProperties, str]]:
        self._assert_valid_args([callsign])
        # NOTE(RKM 2019-11-20) This should always call through to the actual client
        ac_props = self._aircraft_controls.properties(callsign)
        if not isinstance(ac_props, props.AircraftProperties):
            return ac_props
        self.ac_props[callsign] = ac_props
        return ac_props

    def route(
        self, callsign: types.Callsign
    ) -> Optional[Union[props.AircraftRoute, str]]:
        self._assert_valid_args([callsign])
        # NOTE(RKM 2019-11-20) This should always call through to the actual client
        # TODO(RKM 2019-11-21) Potential bug here: route may return None in some cases
        ac_route = self._aircraft_controls.route(callsign)
        if not isinstance(ac_route, props.AircraftRoute):
            return ac_route
        self.ac_routes[callsign] = ac_route
        return ac_route

    def exists(self, callsign: types.Callsign) -> Union[bool, str]:
        self._assert_valid_args([callsign])
        all_callsings = self.callsigns
        return (
            bool(callsign in all_callsings)
            if isinstance(all_callsings, list)
            else all_callsings
        )

    def clear_caches(self):
        """Clears the caches"""
        self._logger.debug(f"Clearing cached data")
        for callsign in self.ac_props:
            self.ac_props[callsign] = None
        for route in self.ac_routes.values():
            route.current_segment_index = None

    def _assert_valid_args(self, args: list):
        # NOTE(RKM 2019-11-20) We should only fail this check if there's something
        # broken in the API layer
        assert args
        for (idx, arg) in enumerate(args):
            assert arg, f"Invalid argument at position {idx}"

    def store_current_props(self):
        assert self._using_caches()
        self.prev_step_props = copy.deepcopy(self._ac_props)

    def _checked_response(
        self, callsign: types.Callsign, err: Optional[str]
    ) -> Optional[str]:
        if err:
            return err
        self.ac_props[callsign] = None
        return None

    def _set_flight_levels(
        self, data: Dict[types.Callsign, props.AircraftProperties]
    ) -> Dict[types.Callsign, props.AircraftProperties]:
        # TODO(RKM 2019-11-24) Need to fill in from our knowledge of the flight levels
        raise NotImplementedError()
