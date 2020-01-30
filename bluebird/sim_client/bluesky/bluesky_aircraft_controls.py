"""
Contains the AbstractAircraftControls implementation for BlueSky
"""
import logging
import re
import traceback
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

import bluebird.utils.properties as props
import bluebird.utils.types as types
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls
from bluebird.utils.units import KTS_PER_MS
from bluebird.utils.units import METERS_PER_FOOT


_ROUTE_RE = re.compile(r"^(\*?)(\w*):((?:-|.)*)/((?:-|\d)*)$")


class BlueSkyAircraftControls(AbstractAircraftControls):
    """AbstractAircraftControls implementation for BlueSky"""

    @property
    def all_properties(
        self,
    ) -> Union[Dict[types.Callsign, props.AircraftProperties], str]:
        data = self._bluesky_client.aircraft_stream_data
        return self._convert_to_ac_props(data)

    @property
    def callsigns(self) -> Union[List[types.Callsign], str]:
        all_props = self.all_properties
        return all_props if isinstance(all_props, str) else all_props.keys()

    def __init__(self, bluesky_client):
        self._bluesky_client = bluesky_client
        self._logger = logging.getLogger(__name__)
        # TODO(RKM 2019-11-21) Make private and refactor tests
        # self.ac_props: Dict[types.Callsign, Optional[props.AircraftProperties]] = {}
        self.ac_routes: Dict[types.Callsign, props.AircraftRoute] = {}
        # TODO(RKM 2019-11-21) For sandbox mode, need to set-up a timer which clears the
        # cache(s) every n sim-seconds

    def set_cleared_fl(
        self, callsign: types.Callsign, flight_level: types.Altitude, **kwargs
    ) -> Optional[str]:

        vspd = kwargs.get("vspd", "")
        cmd_str = f"ALT {callsign} {flight_level} {vspd}".strip()
        # TODO This can also return list (multiple errors?)
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def set_heading(
        self, callsign: types.Callsign, heading: types.Heading
    ) -> Optional[str]:
        cmd_str = f"HDG {callsign} {heading}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def set_ground_speed(
        self, callsign: types.Callsign, ground_speed: types.GroundSpeed
    ):
        cmd_str = f"SPD {callsign} {ground_speed}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def set_vertical_speed(
        self, callsign: types.Callsign, vertical_speed: types.VerticalSpeed
    ):
        # TODO Correct unit conversion for BlueSky
        cmd_str = f"VS {callsign} {vertical_speed}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: str
    ) -> Optional[str]:
        cmd_str = f"DIRECT {callsign} {waypoint}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    def create(
        self,
        callsign: types.Callsign,
        ac_type: str,
        position: types.LatLon,
        heading: types.Heading,
        altitude: types.Altitude,
        gspd: types.GroundSpeed,
    ) -> Optional[str]:
        gspd_kts = gspd.meters_per_sec * KTS_PER_MS
        cmd_str = f"CRE {callsign} {ac_type} {position} {heading} {altitude} {gspd_kts}"
        err = self._bluesky_client.send_stack_cmd(cmd_str)
        if err:
            return err
        # TODO(RKM 2019-11-21) BlueSky currently accepts any string as the aircraft type
        # and doesn't return an error (although it logs it to its own console). We could
        # better handle this by pre-fetching a list of supported aircraft types, then
        # checking against it during any CRE request
        return None

    def properties(
        self, callsign: types.Callsign
    ) -> Optional[Union[props.AircraftProperties, str]]:
        all_props = self.all_properties
        if not isinstance(all_props, dict):
            return all_props
        return all_props[callsign]

    def exists(self, callsign: types.Callsign) -> Union[bool, str]:
        all_callsings = self.callsigns
        return (
            bool(callsign in all_callsings)
            if isinstance(all_callsings, list)
            else all_callsings
        )

    def _convert_to_ac_props(
        self, data: dict,
    ) -> Union[Dict[types.Callsign, props.AircraftProperties], str]:
        ac_props = {}
        try:
            for i in range(len(data["id"])):
                callsign = types.Callsign(data["id"][i])
                ac_props[callsign] = props.AircraftProperties(
                    aircraft_type=data["actype"][i],
                    altitude=types.Altitude(data["alt"][i] / METERS_PER_FOOT),
                    callsign=callsign,
                    cleared_flight_level=None,
                    ground_speed=types.GroundSpeed(int(data["gs"][i])),
                    heading=types.Heading(int(data["trk"][i])),
                    position=types.LatLon(data["lat"][i], data["lon"][i]),
                    requested_flight_level=None,
                    route_name=None,
                    vertical_speed=types.VerticalSpeed(
                        int(data["vs"][i] * 60 / METERS_PER_FOOT)
                    ),
                )
            return ac_props
        except Exception:
            return f"Error parsing ac data from stream: {traceback.format_exc()}"
