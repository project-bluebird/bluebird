"""
Tests for the ProxyAircraftControls class
"""
import copy

import mock
import pytest
from aviary.sector.sector_element import SectorElement

import bluebird.utils.properties as props
import bluebird.utils.types as types
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls
from bluebird.utils.sector_validation import validate_geojson_sector
from tests.data import TEST_SCENARIO
from tests.data import TEST_SECTOR

_TEST_CALLSIGN_1 = types.Callsign("TEST1")
_TEST_CALLSIGN_2 = types.Callsign("TEST2")

_TEST_SECTOR_ELEMENT = validate_geojson_sector(TEST_SECTOR)
assert isinstance(_TEST_SECTOR_ELEMENT, SectorElement)

# TODO (rkm 2020-01-28) Construct these from the test data
_TEST_PROPS = {
    _TEST_CALLSIGN_1: props.AircraftProperties(
        aircraft_type="A380",
        altitude=types.Altitude("FL185"),
        callsign=_TEST_CALLSIGN_1,
        cleared_flight_level=types.Altitude("FL234"),
        ground_speed=types.GroundSpeed(160),
        heading=types.Heading(128),
        position=types.LatLon(23, 45),
        requested_flight_level=types.Altitude("FL250"),
        vertical_speed=types.VerticalSpeed(120),
        route_name=None,
    ),
    _TEST_CALLSIGN_2: props.AircraftProperties(
        aircraft_type="B737",
        altitude=types.Altitude("FL127"),
        callsign=_TEST_CALLSIGN_2,
        cleared_flight_level=types.Altitude("FL100"),
        ground_speed=types.GroundSpeed(160),
        heading=types.Heading(232),
        position=types.LatLon(45, 32),
        requested_flight_level=types.Altitude("FL083"),
        vertical_speed=types.VerticalSpeed(-120),
        route_name=None,
    ),
}

_INVALID_ARG = "Invalid argument at position"


def test_abstract_class_implemented():
    """Tests that ProxyAircraftControls implements the abstract base class"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    ProxyAircraftControls(mock_aircraft_controls)


def test_all_properties():
    """Tests that ProxyAircraftControls implements all_properties"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error handling for the initial population of the aircraft data cache
    mock_all_properties = mock.PropertyMock(return_value="Error")
    type(mock_aircraft_controls).all_properties = mock_all_properties
    all_properties = proxy_aircraft_controls.all_properties
    assert all_properties == "Error"
    assert not proxy_aircraft_controls.ac_props
    mock_all_properties.assert_called_once()

    # Test initial population of the ac_props
    mock_all_properties = mock.PropertyMock(return_value=copy.deepcopy(_TEST_PROPS))
    type(mock_aircraft_controls).all_properties = mock_all_properties
    all_properties = proxy_aircraft_controls.all_properties
    assert all_properties == _TEST_PROPS
    assert proxy_aircraft_controls.ac_props == _TEST_PROPS
    mock_all_properties.assert_called_once()

    # Test use of the cache
    mock_all_properties.reset_mock()
    all_properties = proxy_aircraft_controls.all_properties
    assert all_properties == _TEST_PROPS
    mock_all_properties.assert_not_called()

    # Test re-population of invalidated properties with error
    mock_all_properties.reset_mock()
    mock_properties = mock.Mock(
        sepc=AbstractAircraftControls.properties, return_value="Error"
    )
    proxy_aircraft_controls.properties = mock_properties
    proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1] = None
    all_properties = proxy_aircraft_controls.all_properties
    assert all_properties == "Error"
    mock_properties.assert_called_once_with(_TEST_CALLSIGN_1)
    mock_all_properties.assert_not_called()

    # Test re-population of invalidated properties with no aircraft
    mock_all_properties.reset_mock()
    mock_properties = mock.Mock(
        sepc=AbstractAircraftControls.properties, return_value=None
    )
    proxy_aircraft_controls.properties = mock_properties
    proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1] = None
    all_properties = proxy_aircraft_controls.all_properties
    assert isinstance(all_properties, dict)
    assert len(all_properties) == 1
    assert _TEST_CALLSIGN_1 not in all_properties
    assert all_properties[_TEST_CALLSIGN_2] == _TEST_PROPS[_TEST_CALLSIGN_2]
    mock_properties.assert_called_once_with(_TEST_CALLSIGN_1)
    mock_all_properties.assert_not_called()

    # Test re-population of invalidated properties with a valid aircraft
    mock_all_properties.reset_mock()
    mock_properties = mock.Mock(
        sepc=AbstractAircraftControls.properties,
        return_value=copy.deepcopy(_TEST_PROPS[_TEST_CALLSIGN_1]),
    )
    proxy_aircraft_controls.properties = mock_properties
    proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1] = None
    all_properties = proxy_aircraft_controls.all_properties
    assert isinstance(all_properties, dict)
    assert len(all_properties) == 2
    assert all_properties == _TEST_PROPS
    mock_properties.assert_called_once_with(_TEST_CALLSIGN_1)
    mock_all_properties.assert_not_called()


def test_callsigns():
    """Tests that ProxyAircraftControls implements callsigns"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error handling for the initial population of the aircraft data cache
    mock_all_properties = mock.PropertyMock(return_value="Error")
    type(mock_aircraft_controls).all_properties = mock_all_properties
    callsigns = proxy_aircraft_controls.callsigns
    assert callsigns == "Error"
    assert not proxy_aircraft_controls.ac_props
    mock_all_properties.assert_called_once()

    # Test initial population of the ac_props
    mock_all_properties = mock.PropertyMock(return_value=_TEST_PROPS)
    type(mock_aircraft_controls).all_properties = mock_all_properties
    callsigns = proxy_aircraft_controls.callsigns
    assert callsigns == list(_TEST_PROPS.keys())
    assert proxy_aircraft_controls.ac_props
    mock_all_properties.assert_called_once()

    # Test use of the cache
    mock_all_properties.reset_mock()
    callsigns = proxy_aircraft_controls.callsigns
    assert callsigns == list(_TEST_PROPS.keys())
    mock_all_properties.assert_not_called()


def test_set_cleared_fl():
    """Tests that ProxyAircraftControls implements set_cleared_fl"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    test_altitude = _TEST_PROPS[_TEST_CALLSIGN_1].altitude

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.set_cleared_fl(None, None)  # type: ignore
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 1"):
        proxy_aircraft_controls.set_cleared_fl(_TEST_CALLSIGN_1, None)  # type: ignore

    # Test error handling from set_cleared_fl
    mock_set_cleared_fl = mock.Mock(
        sepc=AbstractAircraftControls.set_cleared_fl, return_value="Error",
    )
    mock_aircraft_controls.set_cleared_fl = mock_set_cleared_fl
    err = proxy_aircraft_controls.set_cleared_fl(_TEST_CALLSIGN_1, test_altitude, a=1)
    assert err == "Error"
    mock_set_cleared_fl.assert_called_once_with(_TEST_CALLSIGN_1, test_altitude, a=1)

    # Test valid request clears the cache value
    mock_set_cleared_fl = mock.Mock(
        sepc=AbstractAircraftControls.set_cleared_fl, return_value=None,
    )
    mock_aircraft_controls.set_cleared_fl = mock_set_cleared_fl
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    err = proxy_aircraft_controls.set_cleared_fl(_TEST_CALLSIGN_1, test_altitude, a=1)
    assert not err
    assert len(proxy_aircraft_controls.ac_props) == 2
    assert not proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1]


def test_set_heading():
    """Tests that ProxyAircraftControls implements set_heading"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    test_heading = _TEST_PROPS[_TEST_CALLSIGN_1].heading

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.set_heading(None, None)  # type: ignore
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 1"):
        proxy_aircraft_controls.set_heading(_TEST_CALLSIGN_1, None)  # type: ignore

    # Test error handling from set_heading
    mock_set_heading = mock.Mock(
        sepc=AbstractAircraftControls.set_heading, return_value="Error",
    )
    mock_aircraft_controls.set_heading = mock_set_heading
    err = proxy_aircraft_controls.set_heading(_TEST_CALLSIGN_1, test_heading)
    assert err == "Error"
    mock_set_heading.assert_called_once_with(_TEST_CALLSIGN_1, test_heading)

    # Test valid request clears the cache value
    mock_set_heading = mock.Mock(
        sepc=AbstractAircraftControls.set_heading, return_value=None,
    )
    mock_aircraft_controls.set_heading = mock_set_heading
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    err = proxy_aircraft_controls.set_heading(_TEST_CALLSIGN_1, test_heading)
    assert not err
    assert len(proxy_aircraft_controls.ac_props) == 2
    assert not proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1]


def test_set_ground_speed():
    """Tests that ProxyAircraftControls implements set_ground_speed"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    test_ground_speed = _TEST_PROPS[_TEST_CALLSIGN_1].ground_speed

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.set_ground_speed(None, None)  # type: ignore
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 1"):
        proxy_aircraft_controls.set_ground_speed(_TEST_CALLSIGN_1, None)  # type: ignore

    # Test error handling from set_ground_speed
    mock_set_ground_speed = mock.Mock(
        sepc=AbstractAircraftControls.set_ground_speed, return_value="Error",
    )
    mock_aircraft_controls.set_ground_speed = mock_set_ground_speed
    err = proxy_aircraft_controls.set_ground_speed(_TEST_CALLSIGN_1, test_ground_speed)
    assert err == "Error"
    mock_set_ground_speed.assert_called_once_with(_TEST_CALLSIGN_1, test_ground_speed)

    # Test valid request clears the cache value
    mock_set_ground_speed = mock.Mock(
        sepc=AbstractAircraftControls.set_ground_speed, return_value=None,
    )
    mock_aircraft_controls.set_ground_speed = mock_set_ground_speed
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    err = proxy_aircraft_controls.set_ground_speed(_TEST_CALLSIGN_1, test_ground_speed)
    assert not err
    assert len(proxy_aircraft_controls.ac_props) == 2
    assert not proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1]


def test_set_vertical_speed():
    """Tests that ProxyAircraftControls implements set_vertical_speed"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    test_vertical_speed = _TEST_PROPS[_TEST_CALLSIGN_1].vertical_speed

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.set_vertical_speed(None, None)  # type: ignore
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 1"):
        proxy_aircraft_controls.set_vertical_speed(
            _TEST_CALLSIGN_1, None  # type: ignore
        )

    # Test error handling from set_vertical_speed
    mock_set_vertical_speed = mock.Mock(
        sepc=AbstractAircraftControls.set_vertical_speed, return_value="Error",
    )
    mock_aircraft_controls.set_vertical_speed = mock_set_vertical_speed
    err = proxy_aircraft_controls.set_vertical_speed(
        _TEST_CALLSIGN_1, test_vertical_speed
    )
    assert err == "Error"
    mock_set_vertical_speed.assert_called_once_with(
        _TEST_CALLSIGN_1, test_vertical_speed
    )

    # Test valid request clears the cache value
    mock_set_vertical_speed = mock.Mock(
        sepc=AbstractAircraftControls.set_vertical_speed, return_value=None,
    )
    mock_aircraft_controls.set_vertical_speed = mock_set_vertical_speed
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    err = proxy_aircraft_controls.set_vertical_speed(
        _TEST_CALLSIGN_1, test_vertical_speed
    )
    assert not err
    assert len(proxy_aircraft_controls.ac_props) == 2
    assert not proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1]


def test_direct_to_waypoint():
    """Tests that ProxyAircraftControls implements direct_to_waypoint"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error for missing aircraft

    err = proxy_aircraft_controls.direct_to_waypoint("INVALID", "")
    assert err == "Unrecognised callsign INVALID"

    # Test error when no route_name

    test_scenario = copy.deepcopy(TEST_SCENARIO)
    test_aircraft_data = test_scenario["aircraft"][0]
    test_callsign = types.Callsign(test_aircraft_data["callsign"])
    test_props = props.AircraftProperties.from_data(test_aircraft_data)
    mock_aircraft_controls.all_properties = {test_callsign: test_props}

    test_aircraft_data.pop("route")
    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, test_scenario)

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
    mock_direct_to_waypoint.assert_called_once_with(test_callsign, "FIYRE")

    # Test valid call

    mock_direct_to_waypoint.reset_mock()
    mock_direct_to_waypoint.return_value = None
    err = proxy_aircraft_controls.direct_to_waypoint(test_callsign, "FIYRE")
    assert not err
    mock_direct_to_waypoint.assert_called_once_with(test_callsign, "FIYRE")


def test_create():
    """Tests that ProxyAircraftControls implements create"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.create(
            None, None, None, None, None, None  # type: ignore
        )
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 1"):
        proxy_aircraft_controls.create(
            _TEST_CALLSIGN_1, None, None, None, None, None  # type: ignore
        )
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 2"):
        proxy_aircraft_controls.create(
            _TEST_CALLSIGN_1, "A380", None, None, None, None  # type: ignore
        )
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 3"):
        proxy_aircraft_controls.create(
            _TEST_CALLSIGN_1,
            "A380",
            types.LatLon(0, 0),
            None,  # type: ignore
            None,  # type: ignore
            None,  # type: ignore
        )
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 4"):
        proxy_aircraft_controls.create(
            _TEST_CALLSIGN_1,
            "A380",
            types.LatLon(0, 0),
            types.Heading(0),
            None,  # type: ignore
            None,  # type: ignore
        )
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 5"):
        proxy_aircraft_controls.create(
            _TEST_CALLSIGN_1,
            "A380",
            types.LatLon(0, 0),
            types.Heading(0),
            types.Altitude(0),
            None,  # type: ignore
        )

    # Test existing callsign
    proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1] = None
    with pytest.raises(AssertionError, match="Aircraft already exists"):
        proxy_aircraft_controls.create(
            _TEST_CALLSIGN_1,
            "A380",
            types.LatLon(0, 0),
            types.Heading(0),
            types.Altitude(0),
            types.GroundSpeed(0),
        )

    # Test error from create
    mock_create = mock.Mock(spec=AbstractAircraftControls.create, return_value="Error")
    mock_aircraft_controls.create = mock_create
    proxy_aircraft_controls.ac_props = {}
    err = proxy_aircraft_controls.create(
        _TEST_CALLSIGN_1,
        "A380",
        types.LatLon(0, 0),
        types.Heading(0),
        types.Altitude(0),
        types.GroundSpeed(0),
    )
    assert err == "Error"
    assert proxy_aircraft_controls.ac_props == {}

    # Test missing properties
    mock_create = mock.Mock(spec=AbstractAircraftControls.create, return_value=None)
    mock_aircraft_controls.create = mock_create
    mock_properties = mock.Mock(
        spec=AbstractAircraftControls.properties, return_value=None
    )
    proxy_aircraft_controls.properties = mock_properties
    with pytest.raises(
        AssertionError, match="Couldn't get properties for newly created aircraft"
    ):
        proxy_aircraft_controls.create(
            _TEST_CALLSIGN_1,
            "A380",
            types.LatLon(0, 0),
            types.Heading(0),
            types.Altitude(0),
            types.GroundSpeed(0),
        )
    assert proxy_aircraft_controls.ac_props == {}

    # Test valid call
    mock_create = mock.Mock(spec=AbstractAircraftControls.create, return_value=None)
    mock_aircraft_controls.create = mock_create
    mock_properties = mock.Mock(
        spec=AbstractAircraftControls.properties,
        return_value=_TEST_PROPS[_TEST_CALLSIGN_1],
    )
    proxy_aircraft_controls.properties = mock_properties
    proxy_aircraft_controls.create(
        _TEST_CALLSIGN_1,
        "A380",
        types.LatLon(0, 0),
        types.Heading(0),
        types.Altitude(0),
        types.GroundSpeed(0),
    )

    # TODO(RKM 2019-11-21) Debug why this doesn't work
    # mock_properties.assert_called_once_with(_TEST_CALLSIGN_1)
    assert mock_properties.call_args[0][0] == types.Callsign("TEST1")

    # Test blank route created
    assert proxy_aircraft_controls.ac_routes[_TEST_CALLSIGN_1] == ...


def test_properties():
    """Tests that ProxyAircraftControls implements properties"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.properties(None)  # type: ignore

    # Test error from properties
    mock_properties = mock.Mock(
        spec=AbstractAircraftControls.properties, return_value="Error"
    )
    mock_aircraft_controls.properties = mock_properties
    err = proxy_aircraft_controls.properties(_TEST_CALLSIGN_1)
    assert err == "Error"

    # Test valid call
    mock_properties = mock.Mock(
        spec=AbstractAircraftControls.properties,
        return_value=_TEST_PROPS[_TEST_CALLSIGN_1],
    )
    mock_aircraft_controls.properties = mock_properties
    props = proxy_aircraft_controls.properties(_TEST_CALLSIGN_1)
    assert props == _TEST_PROPS[_TEST_CALLSIGN_1]

    # Test cache updated
    assert (
        proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1]
        == _TEST_PROPS[_TEST_CALLSIGN_1]
    )


def test_route():
    """Tests that ProxyAircraftControls implements route"""

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test response when no props available

    err = proxy_aircraft_controls.route("TEST")
    assert err == "Unrecognised callsign TEST"

    # Test valid call

    test_aircraft_data = TEST_SCENARIO["aircraft"][0]
    test_callsign = types.Callsign(test_aircraft_data["callsign"])
    test_props = props.AircraftProperties.from_data(test_aircraft_data)
    mock_aircraft_controls.all_properties = {test_callsign: test_props}

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    route = proxy_aircraft_controls.route(test_callsign)
    # TODO(rkm 2020-01-28) Refactor this so it won't break if the test data changes
    assert route == ("ASCENSION", "FIYRE", ["FIYRE", "EARTH", "WATER", "AIR", "SPIRT"])


def test_exists():
    """Tests that ProxyAircraftControls implements exists"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.route(None)  # type: ignore

    # Test missing
    exists = proxy_aircraft_controls.exists(_TEST_CALLSIGN_1)
    assert not exists

    # Test exists
    proxy_aircraft_controls.ac_props[_TEST_CALLSIGN_1] = None
    exists = proxy_aircraft_controls.exists(_TEST_CALLSIGN_1)
    assert exists


def test_invalidate_data():
    raise NotImplementedError()


def test_set_initial_properties():

    mock_aircraft_controls = mock.Mock()
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    test_aircraft_data = TEST_SCENARIO["aircraft"][0]
    test_callsign = types.Callsign(test_aircraft_data["callsign"])
    test_props = props.AircraftProperties.from_data(test_aircraft_data)
    mock_aircraft_controls.all_properties = {test_callsign: test_props}

    proxy_aircraft_controls.set_initial_properties(_TEST_SECTOR_ELEMENT, TEST_SCENARIO)

    assert isinstance(
        proxy_aircraft_controls.properties(test_callsign), props.AircraftProperties
    )
    assert isinstance(proxy_aircraft_controls.route(test_callsign), tuple)
