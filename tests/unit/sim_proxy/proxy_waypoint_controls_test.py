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
