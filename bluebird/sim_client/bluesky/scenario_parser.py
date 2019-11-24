"""
Contains the scenario parser which translates GeoJSON files to the BlueSky format
"""

import bluebird.scenario.sector_element as se

from datetime import datetime, timedelta
import os.path
import numpy as np
import json
import geojson
import jsonpath_rw_ext as jp

from pyproj import Geod
import shapely.geometry as geom

from itertools import chain

BS_PROMPT = ">"
BS_DEFWPT_PREFIX = (
    "00:00:00.00" + BS_PROMPT
)  # TODO: replace this with a generic (not DEFWPT) prefix.
BS_POLY = "POLYALT"
BS_DEFINE_WAYPOINT = "DEFWPT"
BS_CREATE_AIRCRAFT = "CRE"
BS_AIRCRAFT_POSITION = "POS"
BS_FLIGHT_LEVEL = "FL"
BS_ADD_WAYPOINT = "ADDWPT"
BS_ASAS_OFF = "ASAS OFF"
BS_PAN = "PAN"
BS_SCENARIO_EXTENSION = "scn"

JSON_EXTENSION = "json"
CALLSIGN_KEY = "callsign"
TYPE_KEY = "type"
DEPARTURE_KEY = "departure"
DESTINATION_KEY = "destination"
START_POSITION_KEY = "startPosition"
START_TIME_KEY = "startTime"
CURRENT_FLIGHT_LEVEL_KEY = "currentFlightLevel"
CLEARED_FLIGHT_LEVEL_KEY = "clearedFlightLevel"
REQUESTED_FLIGHT_LEVEL_KEY = "requestedFlightLevel"
ROUTE_KEY = "route"
ROUTE_ELEMENT_NAME_KEY = "ROUTE_ELEMENT_NAME"
ROUTE_ELEMENT_TYPE_KEY = "ROUTE_ELEMENT_TYPE"
ROUTE_ELEMENT_SPEED_KEY = "ROUTE_ELEMENT_SPEED"
ROUTE_ELEMENT_LEVEL_KEY = "ROUTE_ELEMENT_LEVEL"
AIRCRAFT_KEY = "aircraft"


class ScenarioParser:
    """
    A parser of geoJSON sectors and JSON scenarios for translation into BlueSky format
    """

    # Default parameters:
    default_speed = 200  # TODO: temporary!

    # TODO. sector_geojson and scenario_json should be connections (or Python
    # equivalent), not strings
    def __init__(self, sector_geojson, scenario_json):

        # Deserialise the sector geoJSON and scenario JSON strings.
        sector = geojson.loads(sector_geojson)

        if se.FEATURES_KEY not in sector:
            raise ValueError(f"Sector geojson must contain {se.FEATURES_KEY} element")

        self.sector = sector

        scenario = json.loads(scenario_json)

        if AIRCRAFT_KEY not in scenario:
            raise ValueError(f"Scenario json must contain {AIRCRAFT_KEY} element")

        self.scenario = scenario

    def features(self):
        return self.sector[se.FEATURES_KEY]

    def features_of_type(self, type_value):
        """
        Filters the features to retain those whose 'type', inside a 'properties'
        element, matches the given type_value. Returns a list of dictionaries
        """

        return [
            properties
            for properties in jp.match("$..{}".format(se.PROPERTIES_KEY), self.sector)
            if properties[se.TYPE_KEY] == type_value
        ]

    def fix_features(self):
        """
        Filters the features to retain those with 'type': 'FIX'.
        Returns a list of dictionaries.
        """

        return self.features_of_type(type_value=se.FIX_VALUE)

    def sector_features(self):
        """
        Filters the features to retain those with 'type': 'SECTOR'.
        Returns a list of dictionaries.
        """

        return self.features_of_type(type_value=se.SECTOR_VALUE)

    def geometries_of_type(self, type_value):
        """
        Filters the features to retain those whose 'type', inside a 'geometry' element,
        matches the given type_value. Returns a list of dictionaries
        """

        return [
            geometry
            for geometry in jp.match("$..{}".format(se.GEOMETRY_KEY), self.sector)
            if geometry[se.TYPE_KEY] == type_value
        ]

    def polygon_geometries(self):

        return self.geometries_of_type(type_value=se.POLYGON_VALUE)

    def sector_polygon(self):

        polygons = self.polygon_geometries()
        if len(polygons) != 1:
            raise Exception(
                "Expected precisely one polygon; found {len(polygons)} polygons."
            )
        return polygons[0]

    def sector_centroid(self):
        """
        Returns the centroid of the sector polygon.
        :return: a shapely.geometry.point.Point object representing the centroid of the
        sector
        """

        # Determine the centroid of the sector polygon.
        coords = self.sector_polygon()[se.COORDINATES_KEY]

        while len(coords) == 1:
            coords = coords[0]

        polygon = geom.Polygon(coords)
        return polygon.centroid

    def polyalt_lines(self):
        """
        Parses a geoJSON sector definition for sector polygon & altitude information and
        returns a list containing a BlueSky POLYALT commands of the form, one for each
        sector in the geoJSON:
        f'00:00:00.00>POLYGON {sector_name} {upper_limit} {lower_limit} {lat1} {lon1}
        ... {latN} {lonN}'
        Currently supports only single-sector scenarios.
        """

        start_time = self.scenario[START_TIME_KEY] + ".00"

        sectors = self.sector_features()
        if len(sectors) != 1:
            raise Exception(
                "Expected precisely one sector; found {len(sectors)} sectors."
            )
        sector = sectors[0]

        polygon = self.sector_polygon()

        sector_name = sector[se.NAME_KEY]
        upper_limit = BS_FLIGHT_LEVEL + str(sector[se.UPPER_LIMIT_KEY][0])
        lower_limit = BS_FLIGHT_LEVEL + str(sector[se.LOWER_LIMIT_KEY][0])

        line = (
            f"{start_time}{BS_PROMPT}{BS_POLY} "
            f"{sector_name} {upper_limit} {lower_limit}"
        )

        # Parse lat/long info.
        for coords_list in polygon[se.COORDINATES_KEY]:

            # Coordinates list may be nested.
            coords = coords_list
            while len(coords) == 1:
                coords = coords[0]

            # Note: longitudes appear first!
            longitudes = [coord[0] for coord in coords]
            latitudes = [coord[1] for coord in coords]

            # Interleave the latitudes and longitudes lists.
            latlongs = [x for latlong in zip(latitudes, longitudes) for x in latlong]

            line = f'{line} {" ".join(str(latlong) for latlong in latlongs)}'

        # Return a list containing the single line.
        return [line]

    def create_aircraft_lines(self):
        """
        Parses a JSON scenario definition for aircraft information and returns a list of
        CRE commands of the form:
        f'HH:MM:SS.00>CRE {callsign} {aircraft_type} {lat} {lon} {heading}
        {flight_level} {knots}'
        """

        aircraft = self.scenario[AIRCRAFT_KEY]

        callsigns = [ac[CALLSIGN_KEY] for ac in aircraft]
        start_times = [
            self.aircraft_start_time(callsign).strftime("%H:%M:%S") + ".00"
            for callsign in callsigns
        ]
        aircraft_types = [ac[TYPE_KEY] for ac in aircraft]

        # TODO: round lat/longs to 6 d.p.
        latitudes = self.aircraft_initial_positions(latitudes=True)
        longitudes = self.aircraft_initial_positions(latitudes=False)
        headings = np.around(self.aircraft_headings()).astype(int)
        flight_levels = [
            BS_FLIGHT_LEVEL + str(ac[CURRENT_FLIGHT_LEVEL_KEY]) for ac in aircraft
        ]
        # TODO. Not given in the JSON. Need to infer from aircraft type. Temporarily set
        # all to the default speed.
        speeds = [ScenarioParser.default_speed] * len(aircraft)

        lines = []
        for i in range(len(start_times)):
            lines.append(
                f"{start_times[i]}{BS_PROMPT}{BS_CREATE_AIRCRAFT} {callsigns[i]} "
                f"{aircraft_types[i]} {latitudes[i]} {longitudes[i]} {headings[i]} "
                f"{flight_levels[i]} {speeds[i]}"
            )
        return lines

    def define_waypoint_lines(self):
        """
        Parses a geoJSON sector definition for waypoint information and returns a list
        of BlueSky DEFWPT commands of the form:
        f'00:00:00.00>DEFWPT {wp_name} {lat} {lon} {wp_type}'
        """

        fixes = self.fix_features()

        wp_names = [fix[se.NAME_KEY] for fix in fixes]
        latitudes = [fix[se.LATITUDE_KEY] for fix in fixes]
        longitudes = [fix[se.LONGITUDE_KEY] for fix in fixes]
        wp_types = [fix[se.TYPE_KEY] for fix in fixes]

        return [
            f"{BS_DEFWPT_PREFIX}{BS_DEFINE_WAYPOINT} {wp_name} {lat} {lon} {wp_type}"
            for wp_name, lat, lon, wp_type in zip(
                wp_names, latitudes, longitudes, wp_types
            )
        ]

    def add_waypoint_lines(self):
        """
        Returns a list of BlueSky add waypoint (ADDWPT) commands of the form:
        f'HH:MM:SS.00>ADDWPT {callsign} {waypoint_name} [{flight_level}]'
        where {flight_level} is optional.
        """

        aircraft = self.scenario[AIRCRAFT_KEY]
        callsigns = [ac[CALLSIGN_KEY] for ac in aircraft]

        nested_list = [
            self.add_aircraft_waypoint_lines(callsign) for callsign in callsigns
        ]

        # Flatten the nested list.
        return list(chain.from_iterable(nested_list))

    def add_aircraft_waypoint_lines(self, callsign):
        """
        Returns a list of BlueSky add waypoint (ADDWPT) commands, for a particular
        aircraft, of the form:
        f'HH:MM:SS.00>ADDWPT {callsign} {waypoint_name} [{flight_level}]'
        where {flight_level} is optional.
        """

        aircraft_start_time = self.aircraft_start_time(callsign)

        # Wait for 1 second after aircraft creation before adding waypoints to its route
        add_waypoint_time = aircraft_start_time + timedelta(seconds=1)
        start_time = add_waypoint_time.strftime("%H:%M:%S") + ".00"

        route = self.route(callsign)

        # Repeat the same callsign for all add waypoint commands.
        # The first waypoint on the route is the initial position, so we only add the
        # others
        callsigns = [callsign] * (len(route) - 1)

        # Get the list of waypoint names on the route, omitting the first one (the
        # initial position)
        waypoint_names = [
            route_element[ROUTE_ELEMENT_NAME_KEY] for route_element in route[1:]
        ]

        # Include flight levels only if the ROUTE_ELEMENT_LEVEL is non-zero.
        flight_levels_parsed = [
            route_element[ROUTE_ELEMENT_LEVEL_KEY] for route_element in route[1:]
        ]
        flight_levels = [" " + str(x) if x != 0 else "" for x in flight_levels_parsed]

        return [
            (
                f"{start_time}{BS_PROMPT}{BS_ADD_WAYPOINT} {callsign} {waypoint_name} "
                f"{flight_level}"
            )
            for callsign, waypoint_name, flight_level in zip(
                callsigns, waypoint_names, flight_levels
            )
        ]

    def asas_off_lines(self):
        """
        Returns a list containing a single BlueSky ASAS OFF command.
        """

        start_time = self.scenario[START_TIME_KEY] + ".00"
        return [f"{start_time}{BS_PROMPT}{BS_ASAS_OFF}"]

    def pan_lines(self):
        """
        Returns a list containing a single BlueSky PAN command of the form:
        00:00:00.00>PAN {lat} {long}
        """

        centroid_coords = self.sector_centroid().coords[0]

        latitude = centroid_coords[1]
        longitude = centroid_coords[0]

        start_time = self.scenario[START_TIME_KEY] + ".00"
        return [f"{start_time}{BS_PROMPT}{BS_PAN} {latitude} {longitude}"]

    def all_lines(self):
        """
        Returns a list containing all lines in the BlueSky scenario, sorted by timestamp
        """

        lines = []
        lines.extend(self.pan_lines())
        lines.extend(self.polyalt_lines())
        lines.extend(self.define_waypoint_lines())
        lines.extend(self.create_aircraft_lines())
        lines.extend(self.add_waypoint_lines())
        lines.extend(self.asas_off_lines())

        # Sort lines by timestamp only (*not* the whole line else waypoints are added in
        # incorrect order). BlueSky expects this and will behave erratically if they're
        # not properly sorted
        return sorted(lines, key=lambda x: x[: len(BS_DEFWPT_PREFIX)])

    def write_bluesky_scenario(self, filename, path="."):

        extension = os.path.splitext(filename)[1]
        if extension.lower() != BS_SCENARIO_EXTENSION.lower():
            filename = filename + "." + BS_SCENARIO_EXTENSION

        file = os.path.join(path, filename)
        with open(file, "w") as f:
            for item in self.all_lines():
                f.write("%s\n" % item)

    def aircraft_property(self, callsign, property_key):
        """
        Parses the JSON scenario definition to extract a particular JSON element for the
        given aircraft
        :param callsign: an aircraft callsign
        """

        ret = [
            aircraft[property_key]
            for aircraft in jp.match("$..{}".format(AIRCRAFT_KEY), self.scenario)[0]
            if aircraft[CALLSIGN_KEY] == callsign
        ]

        if len(ret) != 1:
            raise Exception(
                f"Expected a single aircraft property {property_key} for aircraft "
                f"{callsign}. Found {len(ret)}"
            )

        return ret[0]

    def route(self, callsign):
        """
        Parses the JSON scenario definition to extract the route JSON element for the
        given aircraft
        :param callsign: an aircraft callsign
        """

        return self.aircraft_property(callsign=callsign, property_key=ROUTE_KEY)

    def aircraft_initial_positions(self, latitudes=True):
        """Get the latitudes (or longitudes) of all aircraft in the scenario"""

        # Get the name of the waypoint at which each aircraft starts.
        start_positions = [ac[START_POSITION_KEY] for ac in self.scenario[AIRCRAFT_KEY]]

        key = se.LATITUDE_KEY
        if not latitudes:
            key = se.LONGITUDE_KEY

        return [self.waypoint_properties(name)[key] for name in start_positions]

    def waypoint_properties(self, name):
        """Get the properties of a waypoint by name"""

        fixes = self.fix_features()
        matching_fixes = [fix for fix in fixes if fix[se.NAME_KEY] == name]

        if len(matching_fixes) != 1:
            raise ValueError(f"Invalid waypoint name: {name}")

        return matching_fixes[0]

    def aircraft_start_time(self, callsign):
        """
        Returns the datetime object representing the given aircraft's *absolute* start
        time
        """

        # Get the *relative* aircraft start times (in seconds).
        aircraft_start_time = self.aircraft_property(
            callsign=callsign, property_key=START_TIME_KEY
        )

        # Get the scenario start time as a datetime.
        scenario_start_time = datetime.strptime(
            self.scenario[START_TIME_KEY], "%H:%M:%S"
        )

        # Return the *absolute* aircraft start time.
        return scenario_start_time + timedelta(seconds=aircraft_start_time)

    def aircraft_headings(self):

        aircraft = self.scenario[AIRCRAFT_KEY]

        from_waypoints = [ac[START_POSITION_KEY] for ac in aircraft]
        # To find the to_waypoints, use the *second* waypoint on each aircraft's route.
        to_waypoints = [
            self.route(ac[CALLSIGN_KEY])[1][ROUTE_ELEMENT_NAME_KEY] for ac in aircraft
        ]

        return [
            self.bearing(from_wpt, to_wpt)
            for from_wpt, to_wpt in zip(from_waypoints, to_waypoints)
        ]

    def bearing(self, from_waypoint, to_waypoint):
        """Computes the compass bearing between two waypoints"""

        geodesic = Geod(ellps=se.ELLIPSOID)

        from_properties = self.waypoint_properties(from_waypoint)
        from_lat = from_properties[se.LATITUDE_KEY]
        from_long = from_properties[se.LONGITUDE_KEY]

        to_properties = self.waypoint_properties(to_waypoint)
        to_lat = to_properties[se.LATITUDE_KEY]
        to_long = to_properties[se.LONGITUDE_KEY]

        # Note: order of arguments is long, lat.
        fwd_azimuth, back_azimuth, distance = geodesic.inv(
            from_long, from_lat, to_long, to_lat
        )

        return fwd_azimuth
