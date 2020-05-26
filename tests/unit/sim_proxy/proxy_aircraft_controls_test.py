"""
Tests for the ProxyAircraftControls class
"""
import copy
from unittest import mock

import pytest
from aviary.sector.sector_element import SectorElement

import bluebird.utils.properties as props
import bluebird.utils.types as types
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.utils.sector_validation import validate_geojson_sector
from tests.data import TEST_SCENARIO
from tests.data import TEST_SECTOR


_TEST_SECTOR_ELEMENT = validate_geojson_sector(TEST_SECTOR)
assert isinstance(_TEST_SECTOR_ELEMENT, SectorElement)


@pytest.fixture(scope="function")
def scenario_test_data():
    routes = {}
    for route in _TEST_SECTOR_ELEMENT.routes():
        routes[route.name] = route
    full_data = {}
    sim_data = {}
    for aircraft_data in TEST_SCENARIO["aircraft"]:
        aircraft_props = props.AircraftProperties.from_data(aircraft_data)
        callsign = aircraft_props.callsign
        aircraft_props.route_name = next(
            x
            for x in routes
            if routes[x].fix_names() == [x["fixName"] for x in aircraft_data["route"]]
        )
        full_data[callsign] = copy.deepcopy(aircraft_props)
        # Delete the stuff which isn't set by the simulators
        aircraft_props.cleared_flight_level = None
        aircraft_props.requested_flight_level = None
        aircraft_props.route_name = None
        sim_data[callsign] = aircraft_props
    return full_data, sim_data


def test_abstract_class_implemented():
    """Tests that ProxyAircraftControls implements the abstract base class"""
    ProxyAircraftControls(mock.Mock())


def test_all_properties(scenario_test_data):
    """Tests that ProxyAircraftControls implements all_properties"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    # Test error handling from all_properties

    all_properties_mock = mock.PropertyMock(return_value="Sim error")
    type(mock_aircraft_controls).all_properties = all_properties_mock
    err = proxy_aircraft_controls.all_properties
    assert err == "Sim error"

    # Test valid response

    full_data, sim_data = scenario_test_data

    all_properties_mock.return_value = sim_data
    properties = proxy_aircraft_controls.all_properties
    assert properties == full_data

    # Test existing data reused

    all_properties_mock.reset_mock()
    properties = proxy_aircraft_controls.all_properties
    assert properties == full_data
    all_properties_mock.assert_not_called()


def test_callsigns(scenario_test_data):
    """Tests that ProxyAircraftControls implements callsigns"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    # Test error handling

    all_properties_mock = mock.PropertyMock(return_value="Sim error")
    type(mock_aircraft_controls).all_properties = all_properties_mock
    err = proxy_aircraft_controls.callsigns
    assert err == "Sim error"

    # Test valid response

    _, sim_data = scenario_test_data
    all_properties_mock.return_value = sim_data
    callsings = proxy_aircraft_controls.callsigns
    assert callsings == list(sim_data.keys())


def test_set_cleared_fl(scenario_test_data):
    """Tests that ProxyAircraftControls implements set_cleared_fl"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    # Test error handling from set_cleared_fl

    mock_aircraft_controls.set_cleared_fl.return_value = "Sim error"
    err = proxy_aircraft_controls.set_cleared_fl(None, None, test=None)
    assert err == "Sim error"

    # Test valid response

    full_data, sim_data = scenario_test_data
    test_callsign = list(full_data)[0]
    test_alt = types.Altitude(12_345)

    mock_aircraft_controls.set_cleared_fl.return_value = None
    err = proxy_aircraft_controls.set_cleared_fl(test_callsign, test_alt)
    assert not err

    # Assert stored cfl updated

    all_properties_mock = mock.PropertyMock(return_value=sim_data)
    type(mock_aircraft_controls).all_properties = all_properties_mock
    assert (
        proxy_aircraft_controls.all_properties[test_callsign].cleared_flight_level
        == test_alt
    )


def test_set_heading():
    """Tests that ProxyAircraftControls implements set_heading"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error handling

    mock_aircraft_controls.set_heading.return_value = "Sim error"
    err = proxy_aircraft_controls.set_heading(None, None)
    assert err == "Sim error"

    # Test valid response

    mock_aircraft_controls.set_heading.return_value = None
    err = proxy_aircraft_controls.set_heading(None, None)
    assert not err


def test_set_ground_speed():
    """Tests that ProxyAircraftControls implements set_ground_speed"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error handling

    mock_aircraft_controls.set_ground_speed.return_value = "Sim error"
    err = proxy_aircraft_controls.set_ground_speed(None, None)
    assert err == "Sim error"

    # Test valid response

    mock_aircraft_controls.set_ground_speed.return_value = None
    err = proxy_aircraft_controls.set_ground_speed(None, None)
    assert not err


def test_set_vertical_speed():
    """Tests that ProxyAircraftControls implements set_vertical_speed"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error handling

    mock_aircraft_controls.set_vertical_speed.return_value = "Sim error"
    err = proxy_aircraft_controls.set_vertical_speed(None, None)
    assert err == "Sim error"

    # Test valid response

    mock_aircraft_controls.set_vertical_speed.return_value = None
    err = proxy_aircraft_controls.set_vertical_speed(None, None)
    assert not err


def test_direct_to_waypoint(scenario_test_data):
    """Tests that ProxyAircraftControls implements direct_to_waypoint"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error for missing aircraft

    _, sim_data = scenario_test_data
    all_properties_mock = mock.PropertyMock(return_value=sim_data)
    type(mock_aircraft_controls).all_properties = all_properties_mock

    err = proxy_aircraft_controls.direct_to_waypoint("INVALID", "")
    assert err == "Unknown callsign INVALID"

    # Test error when no route_name

    test_scenario = copy.deepcopy(TEST_SCENARIO)
    test_scenario["aircraft"][0].pop("route")
    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, test_scenario)

    test_callsign = list(sim_data)[0]
    err = proxy_aircraft_controls.direct_to_waypoint(test_callsign, "")
    assert err == "Aircraft has no route"

    # Test error when waypoint not in route

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)
    err = proxy_aircraft_controls.direct_to_waypoint(test_callsign, "TEST")
    assert (
        err == 'Waypoint "TEST" is not in the route '
        "['FIYRE', 'EARTH', 'WATER', 'AIR', 'SPIRT']"
    )

    # Test error from direct_to_waypoint

    mock_direct_to_waypoint = mock.Mock(return_value="Error")
    mock_aircraft_controls.direct_to_waypoint = mock_direct_to_waypoint
    err = proxy_aircraft_controls.direct_to_waypoint(test_callsign, "FIYRE")
    assert err == "Error"

    # Test valid call

    mock_direct_to_waypoint.return_value = None
    err = proxy_aircraft_controls.direct_to_waypoint(test_callsign, "FIYRE")
    assert not err


def test_create(scenario_test_data):
    """Tests that ProxyAircraftControls implements create"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error when callsign exists

    _, sim_data = scenario_test_data
    test_callsign = list(sim_data)[0]

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    err = proxy_aircraft_controls.create(test_callsign, None, None, None, None, None)
    assert err == "Aircraft already exists"

    # Test error from create

    mock_create = mock.Mock(return_value="Sim error (create)")
    mock_aircraft_controls.create = mock_create

    new_callsign = types.Callsign("NEW")
    err = proxy_aircraft_controls.create(new_callsign, None, None, None, None, None)
    assert err == "Sim error (create)"

    # Test error when checking for sim data for new aircraft

    all_properties_mock = mock.PropertyMock(return_value="Sim error (all_properties)")
    type(mock_aircraft_controls).all_properties = all_properties_mock
    mock_create.return_value = None

    err = proxy_aircraft_controls.create(new_callsign, None, None, None, None, None)
    assert err == "Sim error (all_properties)"

    # Test error when no sim data received for newly created aircraft

    new_callsign = types.Callsign("NEW2")
    all_properties_mock.return_value = sim_data
    err = proxy_aircraft_controls.create(new_callsign, None, None, None, None, None)
    assert err == "New callsign missing from sim data"

    # Test valid response

    all_properties_mock.return_value = {
        **sim_data,
        new_callsign: sim_data[test_callsign],
    }

    err = proxy_aircraft_controls.create(new_callsign, None, None, None, None, None)
    assert not err


def test_properties(scenario_test_data):
    """Tests that ProxyAircraftControls implements properties"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error from all_properties

    all_properties_mock = mock.PropertyMock(return_value="Sim error")
    type(mock_aircraft_controls).all_properties = all_properties_mock

    err = proxy_aircraft_controls.properties(None)
    assert err == "Sim error"

    # Test error for unknown callsign

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    full_data, sim_data = scenario_test_data
    all_properties_mock.return_value = sim_data

    err = proxy_aircraft_controls.properties(types.Callsign("MISS"))
    assert err == "Unknown callsign MISS"

    # Test valid response

    test_callsign = list(full_data)[0]
    aircraft_props = proxy_aircraft_controls.properties(test_callsign)
    assert aircraft_props == full_data[test_callsign]


def test_route(scenario_test_data):
    """Tests that ProxyAircraftControls implements route"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error error from properties

    all_properties_mock = mock.PropertyMock(return_value="Sim error")
    type(mock_aircraft_controls).all_properties = all_properties_mock

    err = proxy_aircraft_controls.route(None)
    assert err == "Sim error"

    # Test error when aircraft has no route

    test_scenario = copy.deepcopy(TEST_SCENARIO)
    test_scenario["aircraft"][0].pop("route")
    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, test_scenario)

    full_data, sim_data = scenario_test_data
    test_callsign = list(full_data)[0]
    all_properties_mock.return_value = sim_data

    err = proxy_aircraft_controls.route(test_callsign)
    assert err == "Aircraft has no route"

    # Test valid response

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    err = proxy_aircraft_controls.route(test_callsign)
    route = [x["fixName"] for x in TEST_SCENARIO["aircraft"][0]["route"]]
    assert err == (_TEST_SECTOR_ELEMENT.routes()[0].name, route[0], route)


def test_exists(scenario_test_data):
    """Tests that ProxyAircraftControls implements exists"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error error from callsigns property

    all_properties_mock = mock.PropertyMock(return_value="Sim error")
    type(mock_aircraft_controls).all_properties = all_properties_mock

    err = proxy_aircraft_controls.exists(None)
    assert err == "Sim error"

    # Test False for unknown callsign

    full_data, sim_data = scenario_test_data
    all_properties_mock.return_value = sim_data

    exists = proxy_aircraft_controls.exists(types.Callsign("MISS"))
    assert exists is False

    # Test Tru for known callsign

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    exists = proxy_aircraft_controls.exists(list(full_data)[0])
    assert exists is True


def test_invalidate_data(scenario_test_data):

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Setup valid data

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)
    _, sim_data = scenario_test_data
    all_properties_mock = mock.PropertyMock(return_value=sim_data)
    type(mock_aircraft_controls).all_properties = all_properties_mock

    all_properties = proxy_aircraft_controls.all_properties
    assert isinstance(all_properties, dict)

    # Test data is invalidated

    all_properties_mock.reset_mock()
    proxy_aircraft_controls.invalidate_data()
    all_properties = proxy_aircraft_controls.all_properties
    assert isinstance(all_properties, dict)
    all_properties_mock.assert_called_once()

    # Test data is cleared

    proxy_aircraft_controls.invalidate_data(clear=True)
    all_properties_mock.return_value = {}
    all_properties = proxy_aircraft_controls.all_properties
    assert all_properties == {}
