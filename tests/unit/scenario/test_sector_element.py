
import pytest

import geojson

import bluebird.scenario.sector_shape as ss
import bluebird.scenario.sector_element as se

@pytest.fixture(scope="function")
def i_element():

    name = "i_element"
    origin = (51.5, -0.1275)
    shape = ss.IShape(fix_names=['a', 'b', 'c', 'd', 'e'], route_names = ['up', 'down'])

    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(name, origin, shape, lower_limit, upper_limit)


@pytest.fixture(scope="function")
def x_element():

    name = "HELL"
    origin = (51.5, -0.1275)
    shape = ss.XShape()

    lower_limit = 140
    upper_limit = 400
    return se.SectorElement(name, origin, shape, lower_limit, upper_limit)


def test_boundary_geojson(i_element):

    result = i_element.boundary_geojson()

    assert sorted(result.keys()) == [se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY]
    assert result[se.GEOMETRY_KEY][se.TYPE_KEY] == 'Polygon'

    assert isinstance(result[se.PROPERTIES_KEY], dict)
    assert sorted(result[se.PROPERTIES_KEY].keys()) == \
           sorted([se.NAME_KEY, se.LOWER_LIMIT_KEY, se.ROUTES_KEY, se.TYPE_KEY, se.UPPER_LIMIT_KEY])

    assert isinstance(result[se.PROPERTIES_KEY][se.ROUTES_KEY], dict)
    assert sorted(result[se.PROPERTIES_KEY][se.ROUTES_KEY].keys()) == sorted(i_element.shape.route_names)

def test_waypoint_geojson(i_element):

    name = 'b'.upper()
    result = i_element.waypoint_geojson(name)

    assert sorted(result.keys()) == [se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY]
    assert result[se.GEOMETRY_KEY][se.TYPE_KEY] == 'Point'
    assert result[se.PROPERTIES_KEY][se.NAME_KEY] == name.upper()
    assert result[se.PROPERTIES_KEY][se.TYPE_KEY] == se.FIX_VALUE

def test_route_geojson(i_element):

    #result = i_element.shape.routes()[1][0][1].coords[0][1]
    route_index = 1
    result = i_element.route_geojson(route_index = route_index)

    assert sorted(result.keys()) == [se.GEOMETRY_KEY, se.PROPERTIES_KEY, se.TYPE_KEY]
    assert sorted(result[se.PROPERTIES_KEY]) == [se.LATITUDES_KEY, se.LONGITUDES_KEY, se.NAME_KEY, se.POINTS_KEY, se.TYPE_KEY]
    assert len(result[se.PROPERTIES_KEY][se.LATITUDES_KEY]) == 5
    assert len(result[se.PROPERTIES_KEY][se.LONGITUDES_KEY]) == 5
    assert result[se.PROPERTIES_KEY][se.NAME_KEY] == i_element.shape.route_names[route_index]
    assert len(result[se.PROPERTIES_KEY][se.POINTS_KEY]) == 5
    assert result[se.PROPERTIES_KEY][se.TYPE_KEY] == se.ROUTE_VALUE

    assert isinstance(result[se.GEOMETRY_KEY], dict)
    assert sorted(result[se.GEOMETRY_KEY].keys()) == ['coordinates', se.TYPE_KEY]

    assert isinstance(result[se.GEOMETRY_KEY]['coordinates'], list)
    assert len(result[se.GEOMETRY_KEY]['coordinates']) == len(result[se.PROPERTIES_KEY][se.POINTS_KEY])

    # import pprint
    # pprint.pprint('')
    # pprint.pprint(result)

def test_geo_interface(i_element):

    result = i_element.__geo_interface__

    assert sorted(result.keys()) == [se.FEATURES_KEY]

    # The result contains one feature per route and per waypoint, plus one for the boundary.
    assert len(result[se.FEATURES_KEY]) == len(i_element.shape.route_names) + len(i_element.shape.fixes) + 1

    # import pprint
    # pprint.pprint('')
    # pprint.pprint(result)


def test_serialisation(x_element):
    # Test JSON serialisation/deserialisation.

    serialised = geojson.dumps(x_element, sort_keys=True)

    deserialised = geojson.loads(serialised)

    assert isinstance(deserialised, dict)
    assert list(deserialised.keys()) == [se.FEATURES_KEY]

    # print(serialised)

# def test_write_geojson(x_element):
#     # Test JSON serialisation/deserialisation.
#
#     x_element.write_geojson(filename = "x_sector_hell")