"""
Tests for the ProxyWaypointControls class
"""

import mock
import pytest

import bluebird.utils.types as types
from bluebird.sim_proxy.proxy_waypoint_controls import ProxyWaypointControls
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls


_TEST_WAYPOINTS = [
    types.Waypoint("FIX1", types.LatLon(0, 1), None),
    types.Waypoint("FIX2", types.LatLon(2, 3), types.Altitude("FL120")),
]


def test_abstract_class_implemented():
    """Tests that ProxyWaypointControls implements the abstract base class"""

    mock_waypoint_controls = mock.create_autospec(spec=AbstractWaypointControls)
    ProxyWaypointControls(mock_waypoint_controls)


def test_all_waypoints():
    """Tests that ProxyWaypointControls implements all_waypoints"""

    mock_waypoint_controls = mock.create_autospec(spec=AbstractWaypointControls)
    proxy_waypoint_controls = ProxyWaypointControls(mock_waypoint_controls)

    # Test error handling for the initial population of the waypoints cache
    mock_all_waypoints = mock.PropertyMock(return_value="Error")
    type(mock_waypoint_controls).all_waypoints = mock_all_waypoints
    waypoints = proxy_waypoint_controls.all_waypoints
    assert waypoints == "Error"
    assert not proxy_waypoint_controls._waypoints
    mock_all_waypoints.assert_called_once()

    # Test initial population of the waypoints cache
    mock_all_waypoints = mock.PropertyMock(return_value=_TEST_WAYPOINTS)
    type(mock_waypoint_controls).all_waypoints = mock_all_waypoints
    waypoints = proxy_waypoint_controls.all_waypoints
    assert waypoints == _TEST_WAYPOINTS
    assert proxy_waypoint_controls._waypoints == _TEST_WAYPOINTS
    mock_all_waypoints.assert_called_once()

    # Test use of the cache
    mock_all_waypoints.reset_mock()
    waypoints = proxy_waypoint_controls.all_waypoints
    assert waypoints == _TEST_WAYPOINTS
    mock_all_waypoints.assert_not_called()


def test_find():
    """Tests that ProxyWaypointControls implements find"""

    mock_waypoint_controls = mock.create_autospec(spec=AbstractWaypointControls)
    proxy_waypoint_controls = ProxyWaypointControls(mock_waypoint_controls)

    # Test find with invalid args
    with pytest.raises(AssertionError, match="Must provide a waypoint_name"):
        proxy_waypoint_controls.find(None)
    with pytest.raises(AssertionError, match="Must provide a waypoint_name"):
        proxy_waypoint_controls.find("")

    # Test find with no waypoints
    res = proxy_waypoint_controls.find("FIX1")
    assert not res

    # Test find with existing waypoints
    proxy_waypoint_controls._waypoints = _TEST_WAYPOINTS
    res = proxy_waypoint_controls.find("FAKE")
    assert not res
    res = proxy_waypoint_controls.find(_TEST_WAYPOINTS[0].name)
    assert res == _TEST_WAYPOINTS[0]

    # Test that we get a sensible error when we have multiple waypoints of the same name
    proxy_waypoint_controls._waypoints = [_TEST_WAYPOINTS[0], _TEST_WAYPOINTS[0]]
    with pytest.raises(AssertionError, match='Duplicate waypoints with name "FIX1"'):
        proxy_waypoint_controls.find(_TEST_WAYPOINTS[0].name)


def test_define():
    """Tests that ProxyWaypointControls implements define"""

    mock_waypoint_controls = mock.create_autospec(spec=AbstractWaypointControls)
    proxy_waypoint_controls = ProxyWaypointControls(mock_waypoint_controls)

    # Test find with invalid args
    with pytest.raises(AssertionError, match="Must provide a position"):
        proxy_waypoint_controls.define(None, None)

    # Test define with unspecified name but existing LatLon
    proxy_waypoint_controls._waypoints = [_TEST_WAYPOINTS[0]]
    res = proxy_waypoint_controls.define(None, _TEST_WAYPOINTS[0].position)
    assert res == "A waypoint with LatLon 0.000000 1.000000 already exists"

    # Test define with existing name
    res = proxy_waypoint_controls.define(
        _TEST_WAYPOINTS[0].name, _TEST_WAYPOINTS[0].position
    )
    assert res == 'A waypoint named "FIX1" already exists'

    # Test that errors are handled from waypoint_controls.define
    mock_waypoint_controls.define = mock.Mock(
        sepc=AbstractWaypointControls.define, return_value="Error"
    )
    res = proxy_waypoint_controls.define("FIX3", types.LatLon(0, 0), a=1)
    assert res == "Error"

    # Test that we can create a new waypoint
    new_waypoint = types.Waypoint("FIX3", types.LatLon(0, 0), None)
    mock_define = mock.Mock(
        sepc=AbstractWaypointControls.define, return_value=new_waypoint
    )
    mock_waypoint_controls.define = mock_define
    proxy_waypoint_controls._waypoints = []
    res = proxy_waypoint_controls.define("FIX3", types.LatLon(0, 0), a=1)
    assert res == new_waypoint
    mock_define.assert_called_once_with("FIX3", types.LatLon(0, 0), a=1)

    # Test that the newly created waypoint is in the cache
    assert len(proxy_waypoint_controls._waypoints) == 1
    assert proxy_waypoint_controls._waypoints[0] == new_waypoint
