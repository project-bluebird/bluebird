
import pytest

import bluebird.scenario.scenario_parser as sp

import bluebird.scenario.scenario_generator as sg
import bluebird.scenario.sector_element as se

# geoJSON sector obtained by calling geojson.dumps() on an X-shaped SectorElement.
i_sector_geojson = """
{"features": [{"geometry": {"coordinates": [[[-0.12757200371942023, 51.49977529668487], [-0.12757200400194632, 51.49995505931335], [-0.12786002000972838, 51.49995505878434], [-0.1278600207160484, 51.500044940095805], [-0.12757200414321032, 51.500044940624825], [-0.12757200442574027, 51.50022470324227], [-0.1274279955742597, 51.50022470324227], [-0.12742799585678966, 51.500044940624825], [-0.1271399792839516, 51.500044940095805], [-0.12713997999027163, 51.49995505878434], [-0.12742799599805368, 51.49995505931335], [-0.12742799628057977, 51.49977529668487], [-0.12757200371942023, 51.49977529668487]]], "type": "Polygon"}, "properties": {"lower_limit": [140], "name": "HELL", "routes": {"BLASPHEMER": ["SIN", "GATES", "ABYSS", "HAUNT", "LIMBO"], "DAMNATION": ["WITCH", "SIREN", "ABYSS", "DEMON", "SATAN"], "PURGATORY": ["LIMBO", "HAUNT", "ABYSS", "GATES", "SIN"], "REDEMPTION": ["SATAN", "DEMON", "ABYSS", "SIREN", "WITCH"]}, "type": "SECTOR", "upper_limit": [400]}, "type": "Feature"}, {"geometry": {"coordinates": [[-0.1275, 51.499685415389884], [-0.1275, 51.49977529670688], [-0.1275, 51.49999999999135], [-0.1275, 51.50022470326427], [-0.1275, 51.50031458457025]], "type": "LineString"}, "properties": {"latitudes": [51.499685415389884, 51.49977529670688, 51.49999999999135, 51.50022470326427, 51.50031458457025], "longitudes": [-0.1275, -0.1275, -0.1275, -0.1275, -0.1275], "name": "PURGATORY", "points": ["LIMBO", "HAUNT", "ABYSS", "GATES", "SIN"], "type": "ROUTE"}, "type": "Feature"}, {"geometry": {"coordinates": [[-0.1275, 51.50031458457025], [-0.1275, 51.50022470326427], [-0.1275, 51.49999999999135], [-0.1275, 51.49977529670688], [-0.1275, 51.499685415389884]], "type": "LineString"}, "properties": {"latitudes": [51.50031458457025, 51.50022470326427, 51.49999999999135, 51.49977529670688, 51.499685415389884], "longitudes": [-0.1275, -0.1275, -0.1275, -0.1275, -0.1275], "name": "BLASPHEMER", "points": ["SIN", "GATES", "ABYSS", "HAUNT", "LIMBO"], "type": "ROUTE"}, "type": "Feature"}, {"geometry": {"coordinates": [[-0.1280040285080387, 51.499999998911285], [-0.127860020362888, 51.4999999994403], [-0.1275, 51.49999999999135], [-0.12713997963711202, 51.4999999994403], [-0.12699597149196132, 51.499999998911285]], "type": "LineString"}, "properties": {"latitudes": [51.499999998911285, 51.4999999994403, 51.49999999999135, 51.4999999994403, 51.499999998911285], "longitudes": [-0.1280040285080387, -0.127860020362888, -0.1275, -0.12713997963711202, -0.12699597149196132], "name": "DAMNATION", "points": ["WITCH", "SIREN", "ABYSS", "DEMON", "SATAN"], "type": "ROUTE"}, "type": "Feature"}, {"geometry": {"coordinates": [[-0.12699597149196132, 51.499999998911285], [-0.12713997963711202, 51.4999999994403], [-0.1275, 51.49999999999135], [-0.127860020362888, 51.4999999994403], [-0.1280040285080387, 51.499999998911285]], "type": "LineString"}, "properties": {"latitudes": [51.499999998911285, 51.4999999994403, 51.49999999999135, 51.4999999994403, 51.499999998911285], "longitudes": [-0.12699597149196132, -0.12713997963711202, -0.1275, -0.127860020362888, -0.1280040285080387], "name": "REDEMPTION", "points": ["SATAN", "DEMON", "ABYSS", "SIREN", "WITCH"], "type": "ROUTE"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.1275, 51.50031458457025], "type": "Point"}, "properties": {"latitude": 51.50031458457025, "longitude": -0.1275, "name": "SIN", "type": "FIX"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.1275, 51.50022470326427], "type": "Point"}, "properties": {"latitude": 51.50022470326427, "longitude": -0.1275, "name": "GATES", "type": "FIX"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.127860020362888, 51.4999999994403], "type": "Point"}, "properties": {"latitude": 51.4999999994403, "longitude": -0.127860020362888, "name": "SIREN", "type": "FIX"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.1280040285080387, 51.499999998911285], "type": "Point"}, "properties": {"latitude": 51.499999998911285, "longitude": -0.1280040285080387, "name": "WITCH", "type": "FIX"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.1275, 51.49999999999135], "type": "Point"}, "properties": {"latitude": 51.49999999999135, "longitude": -0.1275, "name": "ABYSS", "type": "FIX"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.1275, 51.49977529670688], "type": "Point"}, "properties": {"latitude": 51.49977529670688, "longitude": -0.1275, "name": "HAUNT", "type": "FIX"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.1275, 51.499685415389884], "type": "Point"}, "properties": {"latitude": 51.499685415389884, "longitude": -0.1275, "name": "LIMBO", "type": "FIX"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.12713997963711202, 51.4999999994403], "type": "Point"}, "properties": {"latitude": 51.4999999994403, "longitude": -0.12713997963711202, "name": "DEMON", "type": "FIX"}, "type": "Feature"}, {"geometry": {"coordinates": [-0.12699597149196132, 51.499999998911285], "type": "Point"}, "properties": {"latitude": 51.499999998911285, "longitude": -0.12699597149196132, "name": "SATAN", "type": "FIX"}, "type": "Feature"}]}
"""

# JSON scenario obtained by calling json.dumps() on a Poisson scenario in an X-shaped sector generated using ScenarioGenerator.
i_scenario_json = """
{"aircraft": [{"callsign": "DELTA997", "clearedFlightLevel": 320, "currentFlightLevel": 320, "departure": "DEP", "destination": "DEST", "requestedFlightLevel": 200, "route": [{"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "WITCH", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "SIREN", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "ABYSS", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 200, "ROUTE_ELEMENT_NAME": "DEMON", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 200, "ROUTE_ELEMENT_NAME": "SATAN", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}], "startPosition": "WITCH", "startTime": 7, "type": "B747"}, {"callsign": "EZY745", "clearedFlightLevel": 240, "currentFlightLevel": 240, "departure": "DEP", "destination": "DEST", "requestedFlightLevel": 400, "route": [{"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "SATAN", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "DEMON", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "ABYSS", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 400, "ROUTE_ELEMENT_NAME": "SIREN", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 400, "ROUTE_ELEMENT_NAME": "WITCH", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}], "startPosition": "SATAN", "startTime": 53, "type": "B747"}, {"callsign": "VJ956", "clearedFlightLevel": 240, "currentFlightLevel": 240, "departure": "DEP", "destination": "DEST", "requestedFlightLevel": 400, "route": [{"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "SIN", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "GATES", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 0, "ROUTE_ELEMENT_NAME": "ABYSS", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 400, "ROUTE_ELEMENT_NAME": "HAUNT", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}, {"ROUTE_ELEMENT_LEVEL": 400, "ROUTE_ELEMENT_NAME": "LIMBO", "ROUTE_ELEMENT_SPEED": 0, "ROUTE_ELEMENT_TYPE": "FIX"}], "startPosition": "SIN", "startTime": 112, "type": "B747"}], "startTime": "00:00:00"}
"""

@pytest.fixture(scope="function")
def target():
    return sp.ScenarioParser(i_sector_geojson, i_scenario_json)


def test_features(target):

    result = target.features()
    assert isinstance(result, list)

    # The X-shaped sector contains 14 features: 4 routes, 9 waypoints and 1 geometry.
    assert len(result) == 4 + 9 + 1


def test_features_of_type(target):

    # Get the (singleton) list of sector features.
    result = target.features_of_type(se.SECTOR_VALUE)

    assert isinstance(result, list)
    assert len(result) == 1

    assert isinstance(result[0], dict)
    assert sorted(result[0].keys()) == sorted([se.NAME_KEY, se.LOWER_LIMIT_KEY, se.UPPER_LIMIT_KEY, se.TYPE_KEY, se.ROUTES_KEY])

def test_fix_features(target):

    result = target.fix_features()

    assert isinstance(result, list)
    assert len(result) == 9
    for fix in result:
        assert isinstance(fix, dict)
        assert sorted(fix.keys()) == sorted([se.LATITUDE_KEY, se.LONGITUDE_KEY, se.TYPE_KEY, se.NAME_KEY])

def test_polygon_geometries(target):

    result = target.polygon_geometries()

    assert isinstance(result, list)
    assert len(result) == 1
    assert isinstance(result[0], dict)


def test_polyalt_lines(target):

    result = target.polyalt_lines()

    assert isinstance(result, list)


def test_define_waypoint_lines(target):

    result = target.define_waypoint_lines()

    # The result is a list of BlueSky waypoint definitions (DEFWPT).
    assert isinstance(result, list)
    assert len(result) == 9

    # All waypoint definitions begin with "00:00:00.00>DEFWPT"
    for x in result:
        assert x[0:len(sp.BS_DEFWPT_PREFIX)] == sp.BS_DEFWPT_PREFIX
        assert x[len(sp.BS_DEFWPT_PREFIX):(len(sp.BS_DEFWPT_PREFIX) + len(sp.BS_DEFINE_WAYPOINT))] == sp.BS_DEFINE_WAYPOINT


def test_waypoint_properties(target):

    result = target.waypoint_properties("SIREN")

    assert isinstance(result, dict)
    assert sorted(result.keys()) == sorted([se.LATITUDE_KEY, se.LONGITUDE_KEY, se.NAME_KEY, se.TYPE_KEY])


def test_bearing(target):

    assert target.bearing(from_waypoint = "WITCH", to_waypoint="SIREN") < 1e-3
    assert target.bearing(from_waypoint = "SIREN", to_waypoint="WITCH") + 180 < 1e-3
    assert 90 - target.bearing(from_waypoint = "LIMBO", to_waypoint="HAUNT") < 1e-3
    assert target.bearing(from_waypoint = "HAUNT", to_waypoint="LIMBO") + 90 < 1e-3


def test_route(target):

    result = target.route(callsign = "DELTA997")

    # result is a list of dictionaries, each one a route element
    assert isinstance(result, list)
    assert isinstance(result[0], dict)
    assert sorted(result[0].keys()) == sorted([sg.ROUTE_ELEMENT_NAME_KEY, sg.ROUTE_ELEMENT_LEVEL_KEY,
                                               sg.ROUTE_ELEMENT_TYPE_KEY, sg.ROUTE_ELEMENT_SPEED_KEY])
    # print(result)


def test_create_aircraft_lines(target):

    result = target.create_aircraft_lines()

    # The result is a list of three BlueSky create aircraft commands (CRE).
    assert isinstance(result, list)
    assert len(result) == 3

    # All create aircraft commands begin with "HH:MM:SS.00>CRE"
    for x in result:
        assert x[0:len(sp.BS_DEFWPT_PREFIX)] == sp.BS_DEFWPT_PREFIX
        assert x[len(sp.BS_DEFWPT_PREFIX):(len(sp.BS_DEFWPT_PREFIX) + len(sp.BS_CREATE_AIRCRAFT))] == sp.BS_CREATE_AIRCRAFT

    # print(result)


def test_add_aircraft_waypoint_lines(target):

    result = target.add_aircraft_waypoint_lines(callsign = "DELTA997")

    assert isinstance(result, list)
    assert len(result) == 4 # Routes contain 5 waypoints, including the initial position

def test_add_waypoint_lines(target):

    result = target.add_waypoint_lines()

    assert isinstance(result, list)

    # The test scenario contains 3 aircraft and each route contains 5 waypoints, including the initial position,
    # we expect 4 add waypoint commands per aircraft.
    assert len(result) == 3 * 4


def test_write_bluesky_scenario(target):

    target.write_bluesky_scenario(filename = "x_sector_parsed_scenario")


geojson_full = """{"type": "FeatureCollection",
 "features": [{"type": "Feature",
   "geometry": {"type": "GeometryCollection",
    "geometries": [{"type": "MultiPolygon",
      "coordinates": [(((-0.26525318647460444, 52.95612775773865),
         (-0.2677656248463748, 53.73983781018759),
         (-1.424083915360491, 54.12479865256711),
         (-1.2865127438899502, 54.27017928067869),
         (-0.1275, 53.883943018791406),
         (1.0315127438899503, 54.27017928067869),
         (1.169083915360491, 54.12479865256711),
         (0.012765624846374782, 53.73983781018759),
         (0.01025318647460445, 52.95612775773865),
         (-0.26525318647460444, 52.95612775773865)),)]}]},
   "properties": {"name": "HEAVEN",
    "type": "SECTOR",
    "lower_limit": [180],
    "upper_limit": [280],
    "routes": {"ethereal": ["BISHP", "GHOST", "TRI", "SON", "DEACN"],
  {"type": "Feature",
     "almighty": ["CANON", "GOD", "TRI", "SON", "DEACN"]}}},
   "geometry": {"type": "GeometryCollection",
    "geometries": [{"type": "MultiPolygon",
      "coordinates": [(((-0.2623857061123687, 52.020076889499634),
         (-0.2649276344135991, 52.85213924047134),
         (0.009927634413599113, 52.85213924047134),
         (0.007385706112368722, 52.020076889499634),
         (-0.2623857061123687, 52.020076889499634)),)]}]},
   "properties": {"name": "EARTH",
    "type": "SECTOR",
    "lower_limit": [130],
    "upper_limit": [200],
    "routes": {"ascension": ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"],
     "fallen": ["SPIRT", "AIR", "WATER", "EARTH", "FIYRE"]}}},
  {"type": "Feature",
   "geometry": {"type": "GeometryCollection",
    "geometries": [{"type": "MultiPolygon",
      "coordinates": [(((-0.2596527086555938, 51.08375683891335),
         (-0.2606096218686495, 51.41669370570894),
         (-0.7930278098291629, 51.41488362105511),
         (-0.7954501663840479, 51.581334784207414),
         (-0.2610941438595675, 51.58315350567532),
         (-0.26207557205922527, 51.916052359621695),
         (0.007075572059225247, 51.916052359621695),
         (0.0060941438595674795, 51.58315350567532),
         (0.5404501663840479, 51.581334784207414),
         (0.5380278098291628, 51.41488362105511),
         (0.005609621868649527, 51.41669370570894),
         (0.004652708655593784, 51.08375683891335),
         (-0.2596527086555938, 51.08375683891335)),)]}]},
   "properties": {"name": "HELL",
    "type": "SECTOR",
    "lower_limit": [110],
    "upper_limit": [140],
    "routes": {"purgatory": ["SIREN", "WITCH", "ABYSS", "HAUNT", "LIMBO"],
     "damnation": ["GATES", "ABYSS", "DEMON", "SATAN"],
     "redemption": ["SATAN", "DEMON", "ABYSS", "GATES"],
     "blasphemer": ["LIMBO", "HAUNT", "ABYSS", "WITCH", "SIREN"]}}},
  {"geometry": {"type": "GeometryCollection",
    "geometries": [{"type": "MultiPolygon",
      "coordinates": [(((-1.424083915360491, 51.08375683891335),
         (-1.424083915360491, 54.27017928067869),
         (1.169083915360491, 54.27017928067869),
         (1.169083915360491, 51.08375683891335),
         (-1.424083915360491, 51.08375683891335)),)]}]},
   "type": "Feature",
   "properties": {"type": "FIR",
    "name": "TRIBULATIONS",
    "lower_limit": [110],
    "upper_limit": [280]}},
  [,
  {"type": "Feature",
   "geometry": {"type": "LineString",
    "coordinates": [(-0.1275, 51.916128869951486),
     (-0.1275, 51.49999999999135),
     (-0.1275, 51.08383154960228),
     (-0.1275, 50.91735552314281)]},
   "properties": {"points": ["GATES", "ABYSS", "DEMON", "SATAN"],
    "latitudes": [51.916128869951486,
     51.49999999999135,
     51.08383154960228,
     50.91735552314281],
    "longitudes": [-0.1275, -0.1275, -0.1275, -0.1275],
    "altitudes": [0.0, 0.0, 0.0, 0.0],
    "name": "DAMNATION",
    "type": "ROUTE"}},
  {"type": "Feature",
   "geometry": {"type": "LineString",
    "coordinates": [(-0.1275, 50.91735552314281),
     (-0.1275, 51.08383154960228),
     (-0.1275, 51.49999999999135),
     (-0.1275, 51.916128869951486)]},
   "properties": {"points": ["SATAN", "DEMON", "ABYSS", "GATES"],
    "latitudes": [50.91735552314281,
     51.08383154960228,
     51.49999999999135,
     51.916128869951486],
    "longitudes": [-0.1275, -0.1275, -0.1275, -0.1275],
    "altitudes": [0.0, 0.0, 0.0, 0.0],
    "name": "REDEMPTION",
    "type": "ROUTE"}},
  {"type": "Feature",
   "geometry": {"type": "LineString",
    "coordinates": [(0.8059024169298712, 51.49629572437266),
     (0.5392364352609249, 51.49811000242283),
     (-0.1275, 51.49999999999135),
     (-0.7942364352609249, 51.49811000242283),
     (-1.0609024169298713, 51.49629572437266)]},
   "properties": {"points": ["LIMBO", "HAUNT", "ABYSS", "WITCH", "SIREN"],
    "latitudes": [51.49629572437266,
     51.49811000242283,
     51.49999999999135,
     51.49811000242283,
     51.49629572437266],
    "longitudes": [0.8059024169298712,
     0.5392364352609249,
     -0.1275,
     -0.7942364352609249,
     -1.0609024169298713],
    "altitudes": [0.0, 0.0, 0.0, 0.0, 0.0],
    "name": "BLASPHEMER",
    "type": "ROUTE"}},
  {"type": "Feature",
   "geometry": {"type": "LineString",
    "coordinates": [(-0.1275, 51.85371248999941),
     (-0.1275, 52.020153629437004),
     (-0.1275, 52.43621774630896),
     (-0.1275, 52.85221785616645),
     (-0.1275, 53.018597551414885)]},
   "properties": {"points": ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"],
    "latitudes": [51.85371248999941,
     52.020153629437004,
     52.43621774630896,
     52.85221785616645,
     53.018597551414885],
    "longitudes": [-0.1275, -0.1275, -0.1275, -0.1275, -0.1275],
    "altitudes": [0.0, 0.0, 0.0, 0.0, 0.0],
    "name": "ASCENSION",
    "type": "ROUTE"}},
  {"type": "Feature",
   "geometry": {"type": "LineString",
    "coordinates": [(-0.1275, 53.018597551414885),
     (-0.1275, 52.85221785616645),
     (-0.1275, 52.43621774630896),
     (-0.1275, 52.020153629437004),
     (-0.1275, 51.85371248999941)]},
   "properties": {"points": ["SPIRT", "AIR", "WATER", "EARTH", "FIYRE"],
    "latitudes": [53.018597551414885,
     52.85221785616645,
     52.43621774630896,
     52.020153629437004,
     51.85371248999941],
    "longitudes": [-0.1275, -0.1275, -0.1275, -0.1275, -0.1275],
    "altitudes": [0.0, 0.0, 0.0, 0.0, 0.0],
    "name": "FALLEN",
    "type": "ROUTE"}},
  {"type": "Feature",
   "geometry": {"type": "LineString",
    "coordinates": [(-1.6038334881825176, 54.277918844416064),
     (-1.3554163378097202, 54.197509553699085),
     (-0.12750000000000017, 53.78792800550492),
     (-0.12750000000000017, 52.956206612894995),
     (-0.12750000000000017, 52.78982234612336)]},
   "properties": {"points": ["BISHP", "GHOST", "TRI", "SON", "DEACN"],
    "latitudes": [54.277918844416064,
     54.197509553699085,
     53.78792800550492,
     52.956206612894995,
     52.78982234612336],
    "longitudes": [-1.6038334881825176,
     -1.3554163378097202,
     -0.12750000000000017,
     -0.12750000000000017,
     -0.12750000000000017],
    "altitudes": [0.0, 0.0, 0.0, 0.0, 0.0],
    "name": "ETHEREAL",
    "type": "ROUTE"}},
  {"type": "Feature",
   "geometry": {"type": "LineString",
    "coordinates": [(1.3488334881825166, 54.277918844416064),
     (1.100416337809719, 54.197509553699085),
     (-0.12750000000000017, 53.78792800550492),
     (-0.12750000000000017, 52.956206612894995),
     (-0.12750000000000017, 52.78982234612336)]},
   "properties": {"points": ["CANON", "GOD", "TRI", "SON", "DEACN"],
    "latitudes": [54.277918844416064,
     54.197509553699085,
     53.78792800550492,
     52.956206612894995,
     52.78982234612336],
    "longitudes": [1.3488334881825166,
     1.100416337809719,
     -0.12750000000000017,
     -0.12750000000000017,
     -0.12750000000000017],
    "altitudes": [0.0, 0.0, 0.0, 0.0, 0.0],
    "name": "ALMIGHTY",
    "type": "ROUTE"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 52.08256690115545, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "SIN",
    "latitude": 52.08256690115545,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 51.916128869951486, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "GATES",
    "latitude": 51.916128869951486,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-1.0609024169298713, 51.49629572437266, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "SIREN",
    "latitude": 51.49629572437266,
    "longitude": -1.0609024169298713,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.7942364352609249, 51.49811000242283, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "WITCH",
    "latitude": 51.49811000242283,
    "longitude": -0.7942364352609249,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 51.49999999999135, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "ABYSS",
    "latitude": 51.49999999999135,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (0.5392364352609249, 51.49811000242283, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "HAUNT",
    "latitude": 51.49811000242283,
    "longitude": 0.5392364352609249,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (0.8059024169298712, 51.49629572437266, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "LIMBO",
    "latitude": 51.49629572437266,
    "longitude": 0.8059024169298712,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 51.08383154960228, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "DEMON",
    "latitude": 51.08383154960228,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 50.91735552314281, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "SATAN",
    "latitude": 50.91735552314281,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 53.018597551414885, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "SPIRT",
    "latitude": 53.018597551414885,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 52.85221785616645, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "AIR",
    "latitude": 52.85221785616645,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 52.43621774630896, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "WATER",
    "latitude": 52.43621774630896,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 52.020153629437004, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "EARTH",
    "latitude": 52.020153629437004,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.1275, 51.85371248999941, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "FIYRE",
    "latitude": 51.85371248999941,
    "longitude": -0.1275,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-1.3554163378097202, 54.197509553699085, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "GHOST",
    "latitude": 54.197509553699085,
    "longitude": -1.3554163378097202,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-1.6038334881825176, 54.277918844416064, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "BISHP",
    "latitude": 54.277918844416064,
    "longitude": -1.6038334881825176,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (1.100416337809719, 54.197509553699085, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "GOD",
    "latitude": 54.197509553699085,
    "longitude": 1.100416337809719,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (1.3488334881825166, 54.277918844416064, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "CANON",
    "latitude": 54.277918844416064,
    "longitude": 1.3488334881825166,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.12750000000000017, 53.78792800550492, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "TRI",
    "latitude": 53.78792800550492,
    "longitude": -0.12750000000000017,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.12750000000000017, 52.956206612894995, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "SON",
    "latitude": 52.956206612894995,
    "longitude": -0.12750000000000017,
    "type": "FIX"}},
  {"type": "Feature",
   "geometry": {"type": "Point",
    "coordinates": (-0.12750000000000017, 52.78982234612336, 0.0)},
   "properties": {"altitude_unit": "m",
    "name": "DEACN",
    "latitude": 52.78982234612336,
    "longitude": -0.12750000000000017,
    "type": "FIX"}}]}"""
