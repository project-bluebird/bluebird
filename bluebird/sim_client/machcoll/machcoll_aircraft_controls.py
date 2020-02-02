"""
Contains the AbstractAircraftControls implementation for MachColl
"""
import logging
import traceback
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

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
        _, data = self._mc_client().get_active_flight_states_and_time()
        self._raise_for_no_data(data)
        callsigns = self._mc_client().get_active_callsigns()
        if callsigns is None:
            return {}
        all_props = {}
        for callsign_str in callsigns:
            flight_props = self._mc_client().get_active_flight_by_callsign(callsign_str)
            self._raise_for_no_data(flight_props)
            all_props[props.callsign] = self._parse_aircraft_properties(flight_props)
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
        self, callsign: types.Callsign, waypoint: str
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
            alt = types.Altitude("FL" + str(ac_props["pos"]["afl"]))
            # TODO Check this is appropriate
            rfl_val = ac_props["flight-plan"]["rfl"]
            rfl = types.Altitude("FL" + str(rfl_val)) if rfl_val else alt
            # TODO Not currently available: gs, hdg, pos, vs
            return props.AircraftProperties(
                aircraft_type=ac_props["flight-data"]["type"],
                altitude=alt,
                callsign=types.Callsign(ac_props["flight-data"]["callsign"]),
                cleared_flight_level=types.Altitude(
                    "FL" + str(ac_props["instruction"]["cfl"])
                ),
                ground_speed=types.GroundSpeed(ac_props["pos"]["speed"]),
                heading=types.Heading(0),
                position=types.LatLon(ac_props["pos"]["lat"], ac_props["pos"]["long"]),
                requested_flight_level=rfl,
                route_name=None,
                vertical_speed=types.VerticalSpeed(0),
            )
        except Exception:
            return f"Error parsing AircraftProperties: {traceback.format_exc()}"

    @staticmethod
    def _raise_for_no_data(data) -> None:
        assert data is not None, "No data received from the simulator"
