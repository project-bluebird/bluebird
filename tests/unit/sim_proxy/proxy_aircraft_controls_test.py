"""
Tests for the ProxyAircraftControls class
"""

import copy

import mock
import pytest

import bluebird.utils.properties as props
import bluebird.utils.types as types
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls

_TEST_CALLSIGN_1 = types.Callsign("TEST1")
_TEST_CALLSIGN_2 = types.Callsign("TEST2")


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
    ),
}

_TEST_WAYPOINT_1 = types.Waypoint("FIX1", types.LatLon(0, 0), altitude=None)

_TEST_ROUTES = {
    _TEST_CALLSIGN_1: props.AircraftRoute(_TEST_CALLSIGN_1, [], 0),
    _TEST_CALLSIGN_2: props.AircraftRoute(
        callsign=_TEST_CALLSIGN_2,
        segments=[
            props.RouteItem(_TEST_WAYPOINT_1, required_gspd=None),
            props.RouteItem(
                types.Waypoint("FIX2", types.LatLon(1, 1), altitude=None),
                required_gspd=None,
            ),
        ],
        current_segment_index=1,
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


def test_all_routes():
    """Tests that ProxyAircraftControls implements all_routes"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test error handling for the initial population of the aircraft route cache
    mock_all_routes = mock.PropertyMock(return_value="Error")
    type(mock_aircraft_controls).all_routes = mock_all_routes
    all_routes = proxy_aircraft_controls.all_routes
    assert all_routes == "Error"
    assert not proxy_aircraft_controls.ac_routes
    mock_all_routes.assert_called_once()

    # Test initial population of ac_routes
    mock_all_routes = mock.PropertyMock(return_value=copy.deepcopy(_TEST_ROUTES))
    type(mock_aircraft_controls).all_routes = mock_all_routes
    all_routes = proxy_aircraft_controls.all_routes
    assert all_routes == _TEST_ROUTES
    assert proxy_aircraft_controls.ac_routes == _TEST_ROUTES
    mock_all_routes.assert_called_once()

    # Test use of the cache
    # Test re-calculation of invalidated route indices
    # Test re-calculation of invalidated route indices with no aircraft
    # Test re-calculation of invalidated route indices with valid aircraft
    pytest.xfail("Need to (re-)implement the calculation of the current route index")


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

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.direct_to_waypoint(None, None)  # type: ignore
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 1"):
        proxy_aircraft_controls.direct_to_waypoint(
            _TEST_CALLSIGN_1, None  # type: ignore
        )

    # Test error for missing aircraft
    proxy_aircraft_controls.ac_props = {}
    test_waypoint = types.Waypoint("FIX3", types.LatLon(0, 0), None)
    with pytest.raises(AssertionError, match="Callsign not in aircraft data"):
        proxy_aircraft_controls.direct_to_waypoint(_TEST_CALLSIGN_1, test_waypoint)

    # Test error for waypoint not in route
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    proxy_aircraft_controls.ac_routes = copy.deepcopy(_TEST_ROUTES)
    err = proxy_aircraft_controls.direct_to_waypoint(_TEST_CALLSIGN_1, test_waypoint)
    assert err == "Waypoint not on the route"

    # Test error from direct_to_waypoint
    mock_direct_to_waypoint = mock.Mock(
        spec=AbstractAircraftControls.direct_to_waypoint, return_value="Error"
    )
    mock_aircraft_controls.direct_to_waypoint = mock_direct_to_waypoint
    err = proxy_aircraft_controls.direct_to_waypoint(_TEST_CALLSIGN_2, _TEST_WAYPOINT_1)
    assert err == "Error"

    # TODO(RKM 2019-11-20) This check fails for some reason, but looks ok in the debug
    # output...
    # mock_direct_to_waypoint.assert_called_once_with(
    #     _TEST_CALLSIGN_2, _TEST_WAYPOINT_1
    # )

    # Test valid call
    mock_direct_to_waypoint = mock.Mock(
        spec=AbstractAircraftControls.direct_to_waypoint, return_value=None
    )
    mock_aircraft_controls.direct_to_waypoint = mock_direct_to_waypoint
    err = proxy_aircraft_controls.direct_to_waypoint(_TEST_CALLSIGN_2, _TEST_WAYPOINT_1)
    assert not err


def test_add_waypoint_to_route():
    """Tests that ProxyAircraftControls implements add_waypoint_to_route"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG}"):
        proxy_aircraft_controls.add_waypoint_to_route(
            None, None, None  # type: ignore
        )
        proxy_aircraft_controls.add_waypoint_to_route(
            _TEST_CALLSIGN_1, None, None  # type: ignore
        )
        proxy_aircraft_controls.add_waypoint_to_route(
            _TEST_CALLSIGN_1, _TEST_WAYPOINT_1, None  # type: ignore
        )

    test_ground_speed = types.GroundSpeed(150)

    # Test missing aircraft
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    with pytest.raises(AssertionError):
        err = proxy_aircraft_controls.add_waypoint_to_route(
            _TEST_CALLSIGN_1, _TEST_WAYPOINT_1, test_ground_speed
        )

    # Test waypoint already on route
    proxy_aircraft_controls.ac_routes = copy.deepcopy(_TEST_ROUTES)
    mock_aircraft_controls
    err = proxy_aircraft_controls.add_waypoint_to_route(
        _TEST_CALLSIGN_2, _TEST_WAYPOINT_1, test_ground_speed
    )
    assert err == "Waypoint already on route"

    # Test error from add_waypoint_to_route
    mock_add_waypoint_to_route = mock.Mock(
        spec=AbstractAircraftControls.add_waypoint_to_route, return_value="Error"
    )
    mock_aircraft_controls.add_waypoint_to_route = mock_add_waypoint_to_route
    err = proxy_aircraft_controls.add_waypoint_to_route(
        _TEST_CALLSIGN_1, _TEST_WAYPOINT_1, test_ground_speed
    )
    assert err == "Error"

    # Test valid call
    mock_add_waypoint_to_route = mock.Mock(
        spec=AbstractAircraftControls.add_waypoint_to_route, return_value=None
    )
    mock_aircraft_controls.add_waypoint_to_route = mock_add_waypoint_to_route
    err = proxy_aircraft_controls.add_waypoint_to_route(
        _TEST_CALLSIGN_1, _TEST_WAYPOINT_1, test_ground_speed
    )
    assert not err

    # Test waypoint appended to route
    last_segment = proxy_aircraft_controls.ac_routes[_TEST_CALLSIGN_1].segments[-1]
    assert last_segment == props.RouteItem(_TEST_WAYPOINT_1, test_ground_speed)


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
    assert proxy_aircraft_controls.ac_routes[_TEST_CALLSIGN_1] == props.AircraftRoute(
        _TEST_CALLSIGN_1, [], None
    )


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

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test invalid args
    with pytest.raises(AssertionError, match=f"{_INVALID_ARG} 0"):
        proxy_aircraft_controls.route(None)  # type: ignore

    # Test error from route
    mock_route = mock.Mock(spec=AbstractAircraftControls.route, return_value="Error")
    mock_aircraft_controls.route = mock_route
    err = proxy_aircraft_controls.route(_TEST_CALLSIGN_1)
    assert err == "Error"

    # Test valid call
    mock_route = mock.Mock(
        spec=AbstractAircraftControls.route, return_value=_TEST_ROUTES[_TEST_CALLSIGN_1]
    )
    mock_aircraft_controls.route = mock_route
    route = proxy_aircraft_controls.route(_TEST_CALLSIGN_1)
    assert route == _TEST_ROUTES[_TEST_CALLSIGN_1]

    # Test cache updated
    assert (
        proxy_aircraft_controls.ac_routes[_TEST_CALLSIGN_1]
        == _TEST_ROUTES[_TEST_CALLSIGN_1]
    )


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


def test_clear_caches():
    """Tests that ProxyAircraftControls implements clear_caches"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    # Test clear_cache clears the route indices
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    proxy_aircraft_controls.ac_routes = copy.deepcopy(_TEST_ROUTES)
    proxy_aircraft_controls.clear_caches()
    ac_props = proxy_aircraft_controls.ac_props
    assert len(ac_props) == len(_TEST_PROPS)
    for prop in ac_props:
        assert ac_props[prop] is None
    ac_routes = proxy_aircraft_controls.ac_routes
    assert len(ac_routes) == len(_TEST_ROUTES)
    for route in ac_routes.values():
        assert route.current_segment_index is None
