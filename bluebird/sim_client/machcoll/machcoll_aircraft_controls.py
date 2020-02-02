"""
Contains the AbstractAircraftControls implementation for MachColl
"""
import logging
import traceback
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from nats.mc_client.mc_client import MCClient
from nats.mc_client.mc_client_metrics import MCClientMetrics

import bluebird.utils.properties as props
import bluebird.utils.types as types
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls


class MachCollAircraftControls(AbstractAircraftControls):
    """AbstractAircraftControls implementation for MachColl"""

    def __init__(self, sim_client):
        self._sim_client = sim_client
        self._logger = logging.getLogger(__name__)

    @property
    def all_properties(
        self,
    ) -> Union[Dict[types.Callsign, props.AircraftProperties], str]:
        # NOTE (rkm 2020-02-02) Would like to use get_active_flight_states_and_time
        # here, but this returns data keyed by the internal identifiers
        callsigns = self._mc_client().get_active_callsigns()
        # NOTE (rkm 2020-02-02) None response form get_active_callsigns may hide
        # connection loss
        if callsigns is None:
            callsigns = []
        all_props = {}
        for callsign_str in callsigns:
            flight_props = self._mc_client().get_active_flight_by_callsign(
                callsign_str,
                [
                    MCClient.FlightPropertiesFilterOption.POS,
                    MCClient.FlightPropertiesFilterOption.FLIGHT_DATA,
                ],
            )
            self._raise_for_no_data(flight_props)
            ac_props = self._parse_aircraft_properties(flight_props)
            if not isinstance(ac_props, props.AircraftProperties):
                return ac_props
            all_props[ac_props.callsign] = ac_props
        return all_props

    @property
    def callsigns(self) -> Union[List[types.Callsign], str]:
        callsigns = self._mc_client().get_active_callsigns()
        self._raise_for_no_data(callsigns)
        if callsigns is None:
            return []
        if not isinstance(callsigns, list):
            return callsigns
        return [types.Callsign(x) for x in callsigns]

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
        return self._not_implemented_response("set_heading")

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        return self._not_implemented_response("set_ground_speed")

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        return self._not_implemented_response("set_vertical_speed")

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: str
    ) -> Optional[str]:
        return self._not_implemented_response("direct_to_waypoint")

    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
        gspd: types.GroundSpeed,
    ) -> Optional[str]:
        return self._not_implemented_response("create")

    def properties(
        self, callsign: types.Callsign
    ) -> Optional[Union[props.AircraftProperties, str]]:
        resp = self._mc_client().get_active_flight_by_callsign(str(callsign))
        self._raise_for_no_data(resp)
        return self._parse_aircraft_properties(resp)

    def exists(self, callsign: types.Callsign) -> Union[bool, str]:
        callsigns = self.callsigns
        if not isinstance(callsigns, list):
            return callsigns
        return callsign in callsigns

    def _mc_client(self) -> MCClientMetrics:
        return self._sim_client.mc_client

    @staticmethod
    def _parse_aircraft_properties(
        ac_props: dict,
    ) -> Union[props.AircraftProperties, str]:
        try:
            # TODO Not currently available: gs, hdg, pos, vs
            return props.AircraftProperties(
                aircraft_type=ac_props["flight-data"]["type"],
                altitude=types.Altitude(f'FL{ac_props["pos"]["afl"]}'),
                callsign=types.Callsign(ac_props["flight-data"]["callsign"]),
                cleared_flight_level=None,
                ground_speed=types.GroundSpeed(ac_props["pos"]["speed"]),
                heading=types.Heading(0),
                initial_flight_level=None,
                position=types.LatLon(ac_props["pos"]["lat"], ac_props["pos"]["long"]),
                requested_flight_level=None,
                route_name=None,
                vertical_speed=types.VerticalSpeed(0),
            )
        except Exception:
            return f"Error parsing AircraftProperties: {traceback.format_exc()}"

    @staticmethod
    def _raise_for_no_data(data) -> None:
        assert data is not None, "No data received from the simulator"

    @staticmethod
    def _not_implemented_response(method: str):
        return f"Error: Method {method} not implemented for MachColl"
