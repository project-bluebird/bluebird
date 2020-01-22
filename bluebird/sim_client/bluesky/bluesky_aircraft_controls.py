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

    @property
    def all_routes(self) -> Union[Dict[types.Callsign, props.AircraftRoute], str]:
        for callsign in self.callsigns:
            route = self.route(callsign)
            if not isinstance(route, props.AircraftRoute):
                return route
            self.ac_routes[callsign] = route
        return self.ac_routes

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

    # NOTE(RKM 2019-11-18) For BlueSky, I think the waypoint has to exist on the
    # aircraft's route
    def direct_to_waypoint(
        self, callsign: types.Callsign, waypoint: types.Waypoint
    ) -> Optional[str]:
        cmd_str = f"DIRECT {callsign} {waypoint}"
        return self._tmp_stack_cmd_handle_list(cmd_str)

    # TODO Check how BlueSky handles the variable length arguments here with LAT LON
    def add_waypoint_to_route(
        self,
        callsign: types.Callsign,
        waypoint: types.Waypoint,
        gspd: types.GroundSpeed,
    ) -> Optional[str]:
        cmd_str = f"ADDWPT {callsign} {waypoint}"
        if waypoint.altitude:
            cmd_str += f" {waypoint.altitude}"
        if gspd:
            cmd_str += f" {gspd}"
        return self._bluesky_client.send_stack_cmd(cmd_str)

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

    def route(
        self, callsign: types.Callsign
    ) -> Optional[Union[props.AircraftRoute, str]]:
        assert callsign
        stack_cmd = f"LISTRTE {callsign}"
        # TODO(RKM 2019-11-23) For large routes, we should check that we wait long
        # enough for BlueSky to send us all the data. If not, we need to update it to
        # send a "stop" message, and then wait to receive that
        route = self._bluesky_client.send_stack_cmd(stack_cmd, response_expected=True)
        if not isinstance(route, list):
            return route
        return self._convert_to_ac_route(callsign, route)

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
                    vertical_speed=types.VerticalSpeed(
                        int(data["vs"][i] * 60 / METERS_PER_FOOT)
                    ),
                    route=None,
                )
            return ac_props
        except Exception:
            return f"Error parsing ac data from stream: {traceback.format_exc()}"

    def _convert_to_ac_route(
        self, callsign: types.Callsign, data: list
    ) -> Optional[Union[props.AircraftRoute, str]]:
        route = props.AircraftRoute(callsign, [], None)
        for idx, line in enumerate(map(lambda s: s.replace(" ", ""), data)):
            match = _ROUTE_RE.match(line)
            if not match:
                return f"Error parsing route: No match for {line}"
            wpt_name = match.group(2)
            # NOTE(RKM 2019-11-23) BlueSky has no consistency...
            req_alt_str = match.group(3) if "-" not in match.group(3) else None
            req_alt = None
            if req_alt_str:
                req_alt = (
                    types.Altitude(req_alt_str)
                    if req_alt_str.startswith("FL")
                    else types.Altitude(int(req_alt_str))
                )
            # TODO(RKM 2019-11-23) Could also get Mach here(?)
            req_gspd = (
                types.GroundSpeed(int(match.group(4)) / KTS_PER_MS)
                if "-" not in match.group(4)
                else None
            )
            # TODO(RKM 2019-11-23) Fill-in the route latlon etc. in the proxy layer
            route.segments.append(
                props.RouteItem(types.Waypoint(wpt_name, None, req_alt), req_gspd)
            )
            if bool(match.group(1)):
                route.current_segment_index = idx
        return route
