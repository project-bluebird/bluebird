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


_TEST_PROPS = {
    types.Callsign("TEST1"): props.AircraftProperties(
        aircraft_type="A380",
        altitude=types.Altitude("FL185"),
        callsign=types.Callsign("TEST1"),
        cleared_flight_level=types.Altitude("FL234"),
        ground_speed=types.GroundSpeed(160),
        heading=types.Heading(128),
        position=types.LatLon(23, 45),
        requested_flight_level=types.Altitude("FL250"),
        vertical_speed=types.VerticalSpeed(120),
    ),
    types.Callsign("TEST2"): props.AircraftProperties(
        aircraft_type="B737",
        altitude=types.Altitude("FL127"),
        callsign=types.Callsign("TEST1"),
        cleared_flight_level=types.Altitude("FL100"),
        ground_speed=types.GroundSpeed(160),
        heading=types.Heading(232),
        position=types.LatLon(45, 32),
        requested_flight_level=types.Altitude("FL083"),
        vertical_speed=types.VerticalSpeed(-120),
    ),
}


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
    test_callsign = list(_TEST_PROPS.keys())[0]
    proxy_aircraft_controls.properties = mock_properties
    proxy_aircraft_controls.ac_props[test_callsign] = None
    all_properties = proxy_aircraft_controls.all_properties
    assert all_properties == "Error"
    mock_properties.assert_called_once_with(test_callsign)
    mock_all_properties.assert_not_called()

    # Test re-population of invalidated properties with no aircraft
    mock_all_properties.reset_mock()
    mock_properties = mock.Mock(
        sepc=AbstractAircraftControls.properties, return_value=None
    )
    proxy_aircraft_controls.properties = mock_properties
    proxy_aircraft_controls.ac_props[test_callsign] = None
    all_properties = proxy_aircraft_controls.all_properties
    assert isinstance(all_properties, dict)
    assert len(all_properties) == 1
    assert not test_callsign in all_properties
    test_callsign_2 = types.Callsign("TEST2")
    assert all_properties[test_callsign_2] == _TEST_PROPS[test_callsign_2]
    mock_properties.assert_called_once_with(test_callsign)
    mock_all_properties.assert_not_called()

    # Test re-population of invalidated properties with a valid aircraft
    mock_all_properties.reset_mock()
    mock_properties = mock.Mock(
        sepc=AbstractAircraftControls.properties,
        return_value=copy.deepcopy(_TEST_PROPS[test_callsign]),
    )
    proxy_aircraft_controls.properties = mock_properties
    proxy_aircraft_controls.ac_props[test_callsign] = None
    all_properties = proxy_aircraft_controls.all_properties
    assert isinstance(all_properties, dict)
    assert len(all_properties) == 2
    assert all_properties == _TEST_PROPS
    mock_properties.assert_called_once_with(test_callsign)
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

    test_callsign = list(_TEST_PROPS.keys())[0]
    test_altitude = _TEST_PROPS[test_callsign].altitude

    # Test invalid args
    with pytest.raises(AssertionError, match="Must provide a valid callsign"):
        proxy_aircraft_controls.set_cleared_fl(None, None)
    with pytest.raises(AssertionError, match="Must provide a valid flight level"):
        proxy_aircraft_controls.set_cleared_fl(test_callsign, None)

    # Test error handling from set_cleared_fl
    mock_set_cleared_fl = mock.Mock(
        sepc=AbstractAircraftControls.set_cleared_fl, return_value="Error",
    )
    mock_aircraft_controls.set_cleared_fl = mock_set_cleared_fl
    err = proxy_aircraft_controls.set_cleared_fl(test_callsign, test_altitude, a=1)
    assert err == "Error"
    mock_set_cleared_fl.assert_called_once_with(test_callsign, test_altitude, a=1)

    # Test valid request clears the cache value
    mock_set_cleared_fl = mock.Mock(
        sepc=AbstractAircraftControls.set_cleared_fl, return_value=None,
    )
    mock_aircraft_controls.set_cleared_fl = mock_set_cleared_fl
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    err = proxy_aircraft_controls.set_cleared_fl(test_callsign, test_altitude, a=1)
    assert not err
    assert len(proxy_aircraft_controls.ac_props) == 2
    assert not proxy_aircraft_controls.ac_props[test_callsign]


def test_set_heading():
    """Tests that ProxyAircraftControls implements set_heading"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    test_callsign = list(_TEST_PROPS.keys())[0]
    test_heading = _TEST_PROPS[test_callsign].heading

    # Test invalid args
    with pytest.raises(AssertionError, match="Must provide a valid callsign"):
        proxy_aircraft_controls.set_heading(None, None)
    with pytest.raises(AssertionError, match="Must provide a valid heading"):
        proxy_aircraft_controls.set_heading(test_callsign, None)

    # Test error handling from set_heading
    mock_set_heading = mock.Mock(
        sepc=AbstractAircraftControls.set_heading, return_value="Error",
    )
    mock_aircraft_controls.set_heading = mock_set_heading
    err = proxy_aircraft_controls.set_heading(test_callsign, test_heading)
    assert err == "Error"
    mock_set_heading.assert_called_once_with(test_callsign, test_heading)

    # Test valid request clears the cache value
    mock_set_heading = mock.Mock(
        sepc=AbstractAircraftControls.set_heading, return_value=None,
    )
    mock_aircraft_controls.set_heading = mock_set_heading
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    err = proxy_aircraft_controls.set_heading(test_callsign, test_heading)
    assert not err
    assert len(proxy_aircraft_controls.ac_props) == 2
    assert not proxy_aircraft_controls.ac_props[test_callsign]


def test_set_ground_speed():
    """Tests that ProxyAircraftControls implements set_ground_speed"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    test_callsign = list(_TEST_PROPS.keys())[0]
    test_ground_speed = _TEST_PROPS[test_callsign].ground_speed

    # Test invalid args
    with pytest.raises(AssertionError, match="Must provide a valid callsign"):
        proxy_aircraft_controls.set_ground_speed(None, None)
    with pytest.raises(AssertionError, match="Must provide a valid ground speed"):
        proxy_aircraft_controls.set_ground_speed(test_callsign, None)

    # Test error handling from set_ground_speed
    mock_set_ground_speed = mock.Mock(
        sepc=AbstractAircraftControls.set_ground_speed, return_value="Error",
    )
    mock_aircraft_controls.set_ground_speed = mock_set_ground_speed
    err = proxy_aircraft_controls.set_ground_speed(test_callsign, test_ground_speed)
    assert err == "Error"
    mock_set_ground_speed.assert_called_once_with(test_callsign, test_ground_speed)

    # Test valid request clears the cache value
    mock_set_ground_speed = mock.Mock(
        sepc=AbstractAircraftControls.set_ground_speed, return_value=None,
    )
    mock_aircraft_controls.set_ground_speed = mock_set_ground_speed
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    err = proxy_aircraft_controls.set_ground_speed(test_callsign, test_ground_speed)
    assert not err
    assert len(proxy_aircraft_controls.ac_props) == 2
    assert not proxy_aircraft_controls.ac_props[test_callsign]


def test_set_vertical_speed():
    """Tests that ProxyAircraftControls implements set_vertical_speed"""

    mock_aircraft_controls = mock.create_autospec(spec=AbstractAircraftControls)
    proxy_aircraft_controls = ProxyAircraftControls(mock_aircraft_controls)

    test_callsign = list(_TEST_PROPS.keys())[0]
    test_vertical_speed = _TEST_PROPS[test_callsign].vertical_speed

    # Test invalid args
    with pytest.raises(AssertionError, match="Must provide a valid callsign"):
        proxy_aircraft_controls.set_vertical_speed(None, None)
    with pytest.raises(AssertionError, match="Must provide a valid vertical speed"):
        proxy_aircraft_controls.set_vertical_speed(test_callsign, None)

    # Test error handling from set_vertical_speed
    mock_set_vertical_speed = mock.Mock(
        sepc=AbstractAircraftControls.set_vertical_speed, return_value="Error",
    )
    mock_aircraft_controls.set_vertical_speed = mock_set_vertical_speed
    err = proxy_aircraft_controls.set_vertical_speed(test_callsign, test_vertical_speed)
    assert err == "Error"
    mock_set_vertical_speed.assert_called_once_with(test_callsign, test_vertical_speed)

    # Test valid request clears the cache value
    mock_set_vertical_speed = mock.Mock(
        sepc=AbstractAircraftControls.set_vertical_speed, return_value=None,
    )
    mock_aircraft_controls.set_vertical_speed = mock_set_vertical_speed
    proxy_aircraft_controls.ac_props = copy.deepcopy(_TEST_PROPS)
    err = proxy_aircraft_controls.set_vertical_speed(test_callsign, test_vertical_speed)
    assert not err
    assert len(proxy_aircraft_controls.ac_props) == 2
    assert not proxy_aircraft_controls.ac_props[test_callsign]
