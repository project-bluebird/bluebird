"""
Tests for BlueSkyAircraftControls
"""
import mock
import pytest

from bluebird.sim_client.bluesky.bluesky_aircraft_controls import (
    BlueSkyAircraftControls,
)
from bluebird.sim_client.bluesky.bluesky_client import BlueSkyClient


def test_abstract_class_implemented():
    """Tests that BlueSkyAircraftControls implements the abstract base class"""

    mock_bs_client = mock.Mock(spec=BlueSkyClient)
    BlueSkyAircraftControls(mock_bs_client)


def test_all_properties():
    """Tests that BlueSkyAircraftControls implements all_properties"""
    pytest.xfail()


def test_callsigns():
    """Tests that BlueSkyAircraftControls implements callsigns"""

    pytest.xfail()


def test_all_routes():
    """Tests that BlueSkyAircraftControls implements all_routes"""
    pytest.xfail()


def test_set_cleared_fl():
    """Tests that BlueSkyAircraftControls implements set_cleared_fl"""
    pytest.xfail()


def test_set_heading():
    """Tests that BlueSkyAircraftControls implements set_heading"""
    pytest.xfail()


def test_set_ground_speed():
    """Tests that BlueSkyAircraftControls implements set_ground_speed"""
    pytest.xfail()


def test_set_vertical_speed():
    """Tests that BlueSkyAircraftControls implements set_vertical_speed"""
    pytest.xfail()


def test_direct_to_waypoint():
    """Tests that BlueSkyAircraftControls implements direct_to_waypoint"""
    pytest.xfail()


def test_add_waypoint_to_route():
    """Tests that BlueSkyAircraftControls implements add_waypoint_to_route"""
    pytest.xfail()


def test_create():
    """Tests that BlueSkyAircraftControls implements create"""
    pytest.xfail()


def test_properties():
    """Tests that BlueSkyAircraftControls implements properties"""
    pytest.xfail()


def test_route():
    """Tests that BlueSkyAircraftControls implements route"""
    pytest.xfail()


def test_exists():
    """Tests that BlueSkyAircraftControls implements exists"""
    pytest.xfail()


def test_clear_caches():
    """Tests that BlueSkyAircraftControls implements clear_caches"""
    pytest.xfail()
