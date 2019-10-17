"""
Construction of I, X, Y airspace sector elements with upper & lower vertical limits.
"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

from pyproj import Proj

from shapely.ops import transform
from shapely.geometry import LineString

from functools import partial

from geojson import dump

import os.path

# CONSTANTS
ELLIPSOID = "WGS84"
GEOJSON_EXTENSION = "geojson"

# JSON keys
FEATURES_KEY = "features"
NAME_KEY = "name"
TYPE_KEY = "type"
PROPERTIES_KEY = "properties"
LOWER_LIMIT_KEY = "lower_limit"
UPPER_LIMIT_KEY = "upper_limit"
ROUTES_KEY = "routes"
GEOMETRY_KEY = "geometry"
COORDINATES_KEY = "coordinates"
LATITUDE_KEY = "latitude"
LONGITUDE_KEY = "longitude"
LATITUDES_KEY = "latitudes"
LONGITUDES_KEY = "longitudes"
POINTS_KEY = "points"

# JSON values
FEATURE_VALUE = "Feature"
SECTOR_VALUE = "SECTOR"
FIX_VALUE = "FIX"
ROUTE_VALUE = "ROUTE"
POLYGON_VALUE = "Polygon"

class SectorElement():
    """An elemental sector of airspace"""

    def __init__(self, name, origin, shape, lower_limit, upper_limit):

        self.name = name

        # Construct the proj-string (see https://proj.org/usage/quickstart.html)
        # Note the unit kmi is "International Nautical Mile" (for full list run $ proj -lu).
        proj_string = f'+proj=stere +lat_0={origin[0]} +lon_0={origin[1]} +k=1 +x_0=0 +y_0=0 +ellps={ELLIPSOID} +units=kmi +no_defs'

        self.projection = Proj(proj_string, preserve_units=True)
        self.shape = shape
        self.lower_limit = lower_limit
        self.upper_limit = upper_limit

    @property
    def __geo_interface__(self) -> dict:
        """
        Return a GeoJSON dictionary representing the geo_interface.
        For serialisation and deserialisation, use geojson.dumps and geojson.loads.
        """

        # Build the list of features: one for the boundary, one for each waypoint and one for each route.
        geojson = {FEATURES_KEY: []}
        geojson[FEATURES_KEY].append(self.boundary_geojson())
        geojson[FEATURES_KEY].extend([self.route_geojson(route_index) for route_index in range(0, len(self.shape.route_names))])
        geojson[FEATURES_KEY].extend([self.waypoint_geojson(name) for name in self.shape.fixes.keys()])

        return geojson

    def boundary_geojson(self) -> dict:
        """Return a GeoJSON dictionary representing the sector boundary"""

        # Lower & upper limits are serialised in a list. TODO. check reason for this.
        geojson = {
            TYPE_KEY: FEATURE_VALUE,
            PROPERTIES_KEY: {
                NAME_KEY: self.name,
                TYPE_KEY: SECTOR_VALUE,
                LOWER_LIMIT_KEY: [self.lower_limit],
                UPPER_LIMIT_KEY: [self.upper_limit],
                ROUTES_KEY: self.shape.named_routes()
            },
            GEOMETRY_KEY: self.__inv_project__(self.shape.polygon).__geo_interface__
        }

        # Fix issue with __geo_interface__ unexpectedly returning a tuple of coordinates rather than a list.
        geojson = self.fix_geometry_coordinates_tuple(geojson)

        return geojson

    def waypoint_geojson(self, name) -> dict:
        """Return a GeoJSON dictionary representing the waypoints"""

        latitude = self.__inv_project__(self.shape.fixes[name]).coords[0][1]
        longitude = self.__inv_project__(self.shape.fixes[name]).coords[0][0]
        geojson = {
            TYPE_KEY: FEATURE_VALUE,
            PROPERTIES_KEY: {
                NAME_KEY: name.upper(),
                LATITUDE_KEY: latitude,
                LONGITUDE_KEY: longitude,
                TYPE_KEY: FIX_VALUE
            },
            GEOMETRY_KEY: self.__inv_project__(self.shape.fixes[name]).__geo_interface__
        }
        return geojson

    def route_geojson(self, route_index) -> dict:
        """
        Returns a GeoJSON dictionary representing a route

        :param route_index: the list index of the route within self.shape.routes()

        A route includes elements:
        - type: "Feature"
        - geometry: a LineString feature whose 'properties' are a list of points, with long/lat repeating those above, plus altitudes
        - properties:
           - points: list of fix names
           - latitudes:
           - longitudes:
           - altitudes:
           - name: e.g. "DAMNATION"
           - type: "ROUTE"
        """

        route = self.shape.routes()[route_index]
        fix_names = [fix_item[0] for fix_item in route]
        latitudes = [self.__inv_project__(fix_item[1]).coords[0][1] for fix_item in route]
        longitudes = [self.__inv_project__(fix_item[1]).coords[0][0] for fix_item in route]
        geojson = {
            TYPE_KEY: FEATURE_VALUE,
            PROPERTIES_KEY: {
                POINTS_KEY: fix_names,
                LATITUDES_KEY: latitudes,
                LONGITUDES_KEY: longitudes,
                NAME_KEY: self.shape.route_names[route_index],
                TYPE_KEY: ROUTE_VALUE
            },
            GEOMETRY_KEY: self.__inv_project__(LineString([fix_item[1] for fix_item in route])).__geo_interface__
        }

        # Fix issue with __geo_interface__ unexpectedly returning a tuple of coordinates rather than a list.
        geojson = self.fix_geometry_coordinates_tuple(geojson)
        return geojson

    def fix_geometry_coordinates_tuple(self, geojson):

        # Fix issue with __geo_interface__ unexpectedly returning a tuple of coordinates rather than a list.
        geojson[GEOMETRY_KEY][COORDINATES_KEY] = list(geojson[GEOMETRY_KEY][COORDINATES_KEY])
        return geojson


    def __inv_project__(self, geom):
        """Helper for doing an inverse projection using the projection system specified above"""
        return transform(partial(self.projection, inverse=True), geom)


    def write_geojson(self, filename, path = "."):

        extension = os.path.splitext(filename)[1]
        if extension.upper() != GEOJSON_EXTENSION:
            filename = filename + "." + GEOJSON_EXTENSION

        file = os.path.join(path, filename)

        with open(file, 'w') as f:
            dump(self, f, indent = 4)
