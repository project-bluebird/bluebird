"""
Construction of 2D polygons (I, X, Y shapes) for use as cross-sections of airspace
sector elements
"""

# author: Tim Hobson
# email: thobson@turing.ac.uk

# TODO: support gluing together simple I, X, Y elements to construct more complex
# sector shape

from enum import Enum

import shapely.geometry as geom
from shapely.ops import cascaded_union
from shapely.affinity import rotate


class SectorType(Enum):
    I = ("I",)  # noqa: E741
    X = ("X",)
    Y = "Y"


class SectorShape:
    """A 2D sector shape with waypoint fixes"""

    airway_width_nm = 10  # Class attribute: constant airway width of 10 nm
    offset_nm = 10  # Class attribute: constant exterior waypoint offset

    # Default fix names:
    i_fix_names = ["spirt", "air", "water", "earth", "fiyre"]
    x_fix_names = [
        "sin",
        "gates",
        "siren",
        "witch",
        "abyss",
        "haunt",
        "limbo",
        "demon",
        "satan",
    ]
    y_fix_names = ["ghost", "bishp", "god", "canon", "tri", "son", "deacn"]

    # Default route names:
    i_route_names = ["ascension", "fallen"]
    x_route_names = ["purgatory", "blasphemer", "damnation", "redemption"]
    y_route_names = ["almighty", "ethereal", "everlasting", "divine"]

    def __init__(
        self,
        sector_type: SectorType,
        polygon: geom.base.BaseGeometry,
        fix_names,
        route_names,
    ):

        if not isinstance(sector_type, SectorType):
            raise KeyError("Type must be a SectorType")

        self._sector_type = sector_type
        self._polygon = polygon

        fix_points = self.__fix_points__()

        if len(fix_names) != len(fix_points):
            raise ValueError(f"fix_names must have length {len(fix_points)}")

        self._fixes = dict(
            zip([fix_name.upper() for fix_name in fix_names], fix_points)
        )

        len_routes = len(self.routes())
        if len(route_names) != len_routes:
            raise ValueError(f"route_names must have length {len_routes}")

        self._route_names = [route_name.upper() for route_name in route_names]

    @property
    def sector_type(self):
        return self._sector_type

    # Make the sector_type property immutable.
    @sector_type.setter
    def sector_type(self, sector_type):
        raise Exception("sector_type is immutable")

    @property
    def polygon(self):
        return self._polygon

    # Make the polygon property immutable.
    @polygon.setter
    def polygon(self, polygon):
        raise Exception("polygon is immutable")

    @property
    def fixes(self):
        return self._fixes

    # Make the fixes property immutable.
    @fixes.setter
    def fixes(self, fixes):
        raise Exception("fixes are immutable")

    @property
    def route_names(self):
        return self._route_names

    # Make the route_names property immutable.
    @route_names.setter
    def route_names(self, route_names):
        raise Exception("route_names are immutable")

    def named_routes(self) -> dict:
        """
        Return a dictionary of routes, mapping from route name to a list of waypoints
        """

        routes = self.routes()
        route_names = self.route_names
        return dict(
            (route_names[route_index], [item[0] for item in routes[route_index]])
            for route_index in range(0, len(routes))
        )


class IShape(SectorShape):
    def __init__(self, length_nm=50, fix_names=None, route_names=None):

        if fix_names is None:
            fix_names = self.i_fix_names

        if route_names is None:
            route_names = self.i_route_names

        # Set the polygon points
        width_nm = SectorShape.airway_width_nm
        points = [
            (-0.5 * width_nm, -0.5 * length_nm),
            (-0.5 * width_nm, 0.5 * length_nm),
            (0.5 * width_nm, 0.5 * length_nm),
            (0.5 * width_nm, -0.5 * length_nm),
        ]

        super(IShape, self).__init__(
            SectorType.I, geom.Polygon(points), fix_names, route_names
        )

    def __fix_points__(self):
        """Compute the locations of the fixes """

        x_min, y_min, x_max, y_max = self.polygon.bounds
        x_mid, y_mid = self.polygon.centroid.coords[0]

        fix_points = [
            geom.Point(x_mid, y_max + self.offset_nm),  # top exterior
            geom.Point(x_mid, y_max),  # top
            geom.Point(x_mid, y_mid),  # middle
            geom.Point(x_mid, y_min),  # bottom
            geom.Point(x_mid, y_min - self.offset_nm),
        ]  # bottom exterior

        return fix_points

    def routes(self):
        """Compute the routes through the sector """

        # Order by increasing y-coordinate to get the "ascending" route.
        ascending_y = sorted(
            list(self.fixes.items()), key=lambda item: item[1].coords[0][1]
        )
        # Reverse the order of fixes to get the "descending" route.
        descending_y = ascending_y[::-1]
        return [ascending_y, descending_y]


class XShape(SectorShape):
    def __init__(self, length_nm=50, fix_names=None, route_names=None):

        if fix_names is None:
            fix_names = self.x_fix_names

        if route_names is None:
            route_names = self.x_route_names

        i = IShape(length_nm)
        polygon = cascaded_union([i.polygon, rotate(i.polygon, 90)])

        super(XShape, self).__init__(SectorType.X, polygon, fix_names, route_names)

    def __fix_points__(self):

        x_mid, y_mid = self.polygon.centroid.coords[0]
        x_min, y_min, x_max, y_max = self.polygon.bounds

        fix_points = [
            geom.Point(x_mid, y_max + self.offset_nm),  # top exterior
            geom.Point(x_mid, y_max),  # top
            geom.Point(x_min, y_mid),  # left
            geom.Point(x_min - self.offset_nm, y_mid),  # left exterior
            geom.Point(x_mid, y_mid),  # middle
            geom.Point(x_mid, y_min),  # bottom
            geom.Point(x_mid, y_min - self.offset_nm),  # bottom exterior
            geom.Point(x_max, y_mid),  # right
            geom.Point(x_max + self.offset_nm, y_mid),
        ]  # right exterior

        return fix_points

    def routes(self, epsilon=1e-10):
        """Compute the routes through the sector """

        # Get the fixes on the vertical line (i.e. with zero x coordinate).
        vertical_fixes = list(
            filter(lambda item: abs(item[1].coords[0][0]) < epsilon, self.fixes.items())
        )
        horizontal_fixes = list(
            filter(lambda item: abs(item[1].coords[0][1]) < epsilon, self.fixes.items())
        )

        # Order by increasing y-coordinate to get the "ascending_y" route.
        ascending_y = sorted(vertical_fixes, key=lambda item: item[1].coords[0][1])
        descending_y = ascending_y[::-1]

        # Order by increasing x-coordinate to get the "ascending_x" route.
        ascending_x = sorted(horizontal_fixes, key=lambda item: item[1].coords[0][0])
        descending_x = ascending_x[::-1]

        return [ascending_y, descending_y, ascending_x, descending_x]


class YShape(SectorShape):
    def __init__(self, length_nm=50, fix_names=None, route_names=None):

        if fix_names is None:
            fix_names = self.y_fix_names

        if route_names is None:
            route_names = self.y_route_names

        # Use an I shape of half length here, so Y sector scale matches that of I & X.
        i = IShape(length_nm / 2)
        x_mid, y_mid = i.polygon.centroid.coords[0]
        x_min, y_min, x_max, y_max = i.polygon.bounds
        polygon = cascaded_union(
            [
                i.polygon,
                rotate(i.polygon, -120, origin=(x_mid, y_max)),
                rotate(i.polygon, 120, origin=(x_mid, y_max)),
            ]
        )

        super(YShape, self).__init__(SectorType.Y, polygon, fix_names, route_names)

    def __fix_points__(self):

        coords = list(self.polygon.boundary.coords)
        xy_min, xy_max = self.minmax_xy(coords)
        xmin, ymin = xy_min
        bottom = self.get_centre(
            [geom.Point(pt) for pt in self.get_coords(coords, xmin)]
        )
        bottom = geom.Point(self.polygon.centroid.coords[0][0], bottom.coords[0][1])
        _x, _y = bottom.coords[0]
        bottom_outer = geom.Point(_x, _y - self.offset_nm)

        origin = self.polygon.centroid
        fix_points = [
            rotate(bottom, -120, origin=origin),  # left
            rotate(bottom_outer, angle=-120, origin=origin),  # left exterior
            rotate(bottom, 120, origin=origin),  # right
            rotate(bottom_outer, angle=120, origin=origin),  # right exterior
            origin,  # middle
            bottom,  # bottom
            bottom_outer,
        ]  # bottom exterior

        return fix_points

    def minmax_xy(self, coords):
        min_x, min_y = min([y for x, y in coords]), min([x for x, y in coords])
        max_x, max_y = max([y for x, y in coords]), max([x for x, y in coords])
        return [(min_x, min_y), (max_x, max_y)]

    def get_coords(self, coords, match):
        return [(x, y) for x, y in coords if x == match or y == match]

    def get_centre(self, coords):
        return geom.Point(geom.GeometryCollection(coords).centroid.coords[0])

    def routes(self, epsilon=1e-10):
        """Compute the routes through the sector """

        # Get the fixes on the vertical line (i.e. with zero x coordinate).
        vertical_fixes = list(
            filter(lambda item: abs(item[1].coords[0][0]) < epsilon, self.fixes.items())
        )

        # Get the fixes on the left arm, possibly including the vertical fixes.
        all_left_fixes = list(
            filter(lambda item: item[1].coords[0][0] < 0, self.fixes.items())
        )

        # Get the fixes strictly on the left arm (not including the vertical fixes).
        left_fixes = list(
            filter(
                lambda item: item[0] not in [it[0] for it in vertical_fixes],
                all_left_fixes,
            )
        )

        # Get the fixes in the route along the left arm.
        left_route_fixes = vertical_fixes
        left_route_fixes.extend(left_fixes)

        # Get the fixes in the route along the right arm.
        right_route_fixes = list(
            filter(
                lambda item: item[0] not in [it[0] for it in left_fixes],
                self.fixes.items(),
            )
        )

        # Order by increasing y-coordinate to get the "ascending_y" route.
        left_ascending_y = sorted(
            left_route_fixes, key=lambda item: item[1].coords[0][1]
        )
        left_descending_y = left_ascending_y[::-1]

        right_ascending_y = sorted(
            right_route_fixes, key=lambda item: item[1].coords[0][1]
        )
        right_descending_y = right_ascending_y[::-1]

        return [
            left_ascending_y,
            left_descending_y,
            right_ascending_y,
            right_descending_y,
        ]
