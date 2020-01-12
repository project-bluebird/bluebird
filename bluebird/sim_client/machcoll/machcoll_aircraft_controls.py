"""
Contains the AbstractAircraftControls implementation for MachColl
"""

import logging
import traceback
from typing import Dict, Optional, Union, List

import bluebird.utils.properties as props
import bluebird.utils.types as types
from bluebird.sim_client.machcoll.machcoll_client_imports import MCClientMetrics
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls


def _raise_for_no_data(data):
    assert data, "No data received from the simulator"


class MachCollAircraftControls(AbstractAircraftControls):
    """
    AbstractAircraftControls implementation for MachColl
    """

    # @property
    # def stream_data(self) -> Optional[List[bb_props.AircraftProperties]]:
    #     raise NotImplementedError

    @property
    def all_properties(
        self,
    ) -> Union[Dict[types.Callsign, props.AircraftProperties], str]:
        self._logger.debug("BlueSkyAircraftControls.all_properties")
        if not self._ac_data:
            simt, data = self._mc_client().get_active_flight_states_and_time()
            if not data:
                return "No data received from MachColl"

        resp = self._mc_client().get_active_callsigns()
        _raise_for_no_data(resp)
        all_props = {}
        for callsign_str in resp:
            callsign = types.Callsign(callsign_str)
            props = self.properties(callsign)
            all_props[callsign] = props
        return all_props

    @property
    def callsigns(self) -> Union[List[types.Callsign], str]:
        all_props = self.all_properties
        return all_props if isinstance(all_props, str) else all_props.keys()

    @property
    def all_routes(self) -> Dict[types.Callsign, props.AircraftRoute]:
        raise NotImplementedError
        resp = self._mc_client().get_active_callsigns()
        _raise_for_no_data(resp)
        routes = {}
        for callsign_str in resp:
            callsign = types.Callsign(callsign_str)
            # TODO: Check that a None response *only* implies a connection error
            route = self._mc_client().get_flight_plan_for_callsign(str(callsign))
            # TODO: Check the type of route
            routes[callsign] = route
        return routes

    def __init__(self, sim_client):
        self._sim_client = sim_client
        self._logger = logging.getLogger(__name__)
        self._ac_data = {}

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:
        err = self._mc_client().set_cfl_for_callsign(
            str(callsign), flight_level.flight_levels
        )
        return str(err) if err else None

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

    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
        gspd: types.GroundSpeed,
    ) -> Optional[str]:
        raise NotImplementedError

    def properties(
        self, callsign: types.Callsign
    ) -> Optional[Union[props.AircraftProperties, str]]:
        raise NotImplementedError
        resp = self._mc_client().get_active_flight_by_callsign(str(callsign))
        _raise_for_no_data(resp)
        return self._parse_aircraft_properties(resp)

    def route(
        self, callsign: types.Callsign
    ) -> Optional[Union[props.AircraftRoute, str]]:
        raise NotImplementedError

    def exists(self, callsign: types.Callsign) -> Union[bool, str]:
        raise NotImplementedError

    def clear_cache(self):
        self._ac_data = {}

    def _mc_client(self) -> MCClientMetrics:
        return self._sim_client.mc_client

    @staticmethod
    def _parse_aircraft_properties(
        ac_props: dict,
    ) -> Union[props.AircraftProperties, str]:
        try:
            alt = types.Altitude("FL" + str(ac_props["pos"]["afl"]))
            # TODO Check this is appropriate
            rfl_val = ac_props["flight-plan"]["rfl"]
            rfl = types.Altitude("FL" + str(rfl_val)) if rfl_val else alt
            # TODO Not currently available: gs, hdg, pos, vs
            return props.AircraftProperties(
                ac_props["flight-data"]["type"],
                alt,
                types.Callsign(ac_props["flight-data"]["callsign"]),
                types.Altitude("FL" + str(ac_props["instruction"]["cfl"])),
                types.GroundSpeed(ac_props["pos"]["speed"]),
                types.Heading(0),
                types.LatLon(ac_props["pos"]["lat"], ac_props["pos"]["long"]),
                rfl,
                types.VerticalSpeed(0),
            )
        except Exception:
            return f"Error parsing AircraftProperties: {traceback.format_exc()}"
