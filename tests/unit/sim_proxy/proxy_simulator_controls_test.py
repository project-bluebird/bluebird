"""
Tests for the ProxySimulatorControls class
"""

import datetime
import logging

import mock
import pytest

import bluebird.utils.properties as props
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.sim_proxy.proxy_simulator_controls import ProxySimulatorControls
from bluebird.utils.abstract_aircraft_controls import AbstractAircraftControls
from bluebird.utils.abstract_simulator_controls import AbstractSimulatorControls
from bluebird.utils.abstract_waypoint_controls import AbstractWaypointControls

# TODO(RKM 2020-01-01) Refactor this
_TEST_SIM_PROPERTIES = props.SimProperties(
    sector_name="test-sector",
    scenario_name="test-scenario",
    scenario_time=0,
    seed=0,
    speed=1.0,
    state=props.SimState.INIT,
    dt=1.0,
    utc_datetime=datetime.datetime.now(),
)

_MOCK_AIRCRAFT_CONTROLS = mock.create_autospec(spec=AbstractAircraftControls)
_MOCK_WAYPOINT_CONTROLS = mock.create_autospec(spec=AbstractWaypointControls)


def test_abstract_class_implemented():
    """Tests that ProxySimulatorControls implements the abstract base class"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )


def test_properties():
    """Tests that ProxySimulatorControls implements properties"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test error handling for the initial population of the properties cache
    mock_properties = mock.PropertyMock(return_value="Error")
    type(mock_simulator_controls).properties = mock_properties
    properties = proxy_simulator_controls.properties
    assert properties == "Error"
    assert not proxy_simulator_controls.sim_props
    mock_properties.assert_called_once()

    # Test initial population of the properties cache
    mock_properties = mock.PropertyMock(return_value=_TEST_SIM_PROPERTIES)
    type(mock_simulator_controls).properties = mock_properties
    properties = proxy_simulator_controls.properties
    assert properties == _TEST_SIM_PROPERTIES
    assert proxy_simulator_controls.sim_props == _TEST_SIM_PROPERTIES
    mock_properties.assert_called_once()

    # Test use of the cache
    mock_properties.reset_mock()
    properties = proxy_simulator_controls.properties
    assert properties == _TEST_SIM_PROPERTIES
    mock_properties.assert_not_called()


def test_load_scenario():
    """Tests that ProxySimulatorControls implements properties"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test arg parsing
    with pytest.raises(AssertionError, match="Must provide a scenario name"):
        proxy_simulator_controls.load_scenario(None)
    with pytest.raises(AssertionError, match="Must provide a scenario name"):
        proxy_simulator_controls.load_scenario("")
    with pytest.raises(AssertionError, match="Speed must be positive"):
        proxy_simulator_controls.load_scenario("TEST", -1)

    # Test error handling from load_scenario
    mock_simulator_controls.load_scenario = mock.Mock(
        sepc=AbstractSimulatorControls.load_scenario, return_value="Error"
    )
    res = proxy_simulator_controls.load_scenario("TEST")
    assert res == "Error"

    # Test load_scenario
    mock_simulator_controls.properties = _TEST_SIM_PROPERTIES
    mock_clear_caches = mock.Mock(
        sepc=ProxyAircraftControls.clear_caches, return_value=None
    )
    _MOCK_AIRCRAFT_CONTROLS.clear_caches = mock_clear_caches
    _MOCK_WAYPOINT_CONTROLS.waypoints = True
    mock_simulator_controls.load_scenario = mock.Mock(
        sepc=AbstractSimulatorControls.load_scenario, return_value=None
    )
    res = proxy_simulator_controls.load_scenario("TEST")
    assert not res
    mock_simulator_controls.load_scenario.assert_called_once_with("TEST", 1.0, False)

    # Check that caches are empty after a new scenario is loaded
    mock_clear_caches.assert_called_once()
    assert not proxy_simulator_controls.sim_props
    assert not _MOCK_WAYPOINT_CONTROLS.waypoints


def test_start():
    """Tests that ProxySimulatorControls implements start"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test error handling from start
    mock_simulator_controls.start = mock.Mock(
        sepc=AbstractSimulatorControls.start, return_value="Error"
    )
    res = proxy_simulator_controls.start()
    assert res == "Error"

    # Test valid response
    mock_simulator_controls.start = mock.Mock(
        sepc=AbstractSimulatorControls.start, return_value=None
    )
    res = proxy_simulator_controls.start()
    assert not res


def test_reset():
    """Tests that ProxySimulatorControls implements reset"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test error handling from reset
    mock_simulator_controls.reset = mock.Mock(
        sepc=AbstractSimulatorControls.reset, return_value="Error"
    )
    res = proxy_simulator_controls.reset()
    assert res == "Error"

    # Test valid response
    mock_simulator_controls.properties = _TEST_SIM_PROPERTIES
    mock_clear_caches = mock.Mock(
        sepc=ProxyAircraftControls.clear_caches, return_value=None
    )
    _MOCK_AIRCRAFT_CONTROLS.clear_caches = mock_clear_caches
    _MOCK_WAYPOINT_CONTROLS.waypoints = True
    mock_simulator_controls.reset = mock.Mock(
        sepc=AbstractSimulatorControls.reset, return_value=None
    )
    res = proxy_simulator_controls.reset()
    assert not res

    # Check that caches are empty after a new scenario is loaded
    assert not proxy_simulator_controls.sim_props
    mock_clear_caches.assert_called_once()
    assert not _MOCK_WAYPOINT_CONTROLS.waypoints


def test_pause():
    """Tests that ProxySimulatorControls implements pause"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test error handling from pause
    mock_simulator_controls.pause = mock.Mock(
        sepc=AbstractSimulatorControls.pause, return_value="Error"
    )
    res = proxy_simulator_controls.pause()
    assert res == "Error"

    # Test valid response
    mock_simulator_controls.pause = mock.Mock(
        sepc=AbstractSimulatorControls.pause, return_value=None
    )
    res = proxy_simulator_controls.pause()
    assert not res


def test_resume():
    """Tests that ProxySimulatorControls implements resume"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test error handling from resume
    mock_simulator_controls.resume = mock.Mock(
        sepc=AbstractSimulatorControls.resume, return_value="Error"
    )
    res = proxy_simulator_controls.resume()
    assert res == "Error"

    # Test valid response
    mock_simulator_controls.resume = mock.Mock(
        sepc=AbstractSimulatorControls.resume, return_value=None
    )
    res = proxy_simulator_controls.resume()
    assert not res


def test_stop():
    """Tests that ProxySimulatorControls implements stop"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test error handling from stop
    mock_simulator_controls.stop = mock.Mock(
        sepc=AbstractSimulatorControls.stop, return_value="Error"
    )
    res = proxy_simulator_controls.stop()
    assert res == "Error"

    # Test valid response
    mock_simulator_controls.stop = mock.Mock(
        sepc=AbstractSimulatorControls.stop, return_value=None
    )
    res = proxy_simulator_controls.stop()
    assert not res


def test_step():
    """Tests that ProxySimulatorControls implements step"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test error handling from step
    mock_simulator_controls.step = mock.Mock(
        sepc=AbstractSimulatorControls.step, return_value="Error"
    )
    res = proxy_simulator_controls.step()
    assert res == "Error"

    # Test valid response
    mock_simulator_controls.properties = _TEST_SIM_PROPERTIES
    mock_clear_caches = mock.Mock(
        sepc=ProxyAircraftControls.clear_caches, return_value=None
    )
    _MOCK_AIRCRAFT_CONTROLS.clear_caches = mock_clear_caches
    _MOCK_WAYPOINT_CONTROLS.waypoints = True
    mock_simulator_controls.step = mock.Mock(
        sepc=AbstractSimulatorControls.step, return_value=None
    )
    _mock_logger = mock.Mock(spec=logging.Logger)
    proxy_simulator_controls._logger = _mock_logger
    res = proxy_simulator_controls.step()
    assert not res

    # Check that caches are empty after a new scenario is loaded
    assert proxy_simulator_controls.sim_props == _TEST_SIM_PROPERTIES
    mock_clear_caches.assert_called_once()
    assert not _MOCK_WAYPOINT_CONTROLS.waypoints

    # Checks that the properties are logged
    _mock_logger.info.assert_called_once_with(
        f"{str(_TEST_SIM_PROPERTIES.utc_datetime)} [   0]  1.0x INIT"
    )


def test_set_speed():
    """Tests that ProxySimulatorControls implements set_speed"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test arg parsing
    with pytest.raises(AssertionError, match="Speed must be positive"):
        proxy_simulator_controls.set_speed(-1.0)

    # Test error handling from set_speed
    mock_simulator_controls.set_speed = mock.Mock(
        sepc=AbstractSimulatorControls.set_speed, return_value="Error"
    )
    res = proxy_simulator_controls.set_speed(1.0)
    assert res == "Error"

    # Test set_speed
    mock_simulator_controls.properties = _TEST_SIM_PROPERTIES
    mock_simulator_controls.set_speed = mock.Mock(
        sepc=AbstractSimulatorControls.set_speed, return_value=None
    )
    res = proxy_simulator_controls.set_speed(1.0)
    assert not res
    mock_simulator_controls.set_speed.assert_called_once_with(1.0)

    # Check that cache is empty after a new scenario is loaded
    assert not proxy_simulator_controls.sim_props


def test_set_seed():
    """Tests that ProxySimulatorControls implements set_seed"""

    mock_simulator_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_simulator_controls, _MOCK_AIRCRAFT_CONTROLS, _MOCK_WAYPOINT_CONTROLS
    )

    # Test arg parsing
    with pytest.raises(AssertionError, match="Invalid seed"):
        proxy_simulator_controls.set_seed(-1)

    # Test error handling from set_seed
    mock_simulator_controls.set_seed = mock.Mock(
        sepc=AbstractSimulatorControls.set_seed, return_value="Error"
    )
    res = proxy_simulator_controls.set_seed(1)
    assert res == "Error"

    # Test set_seed
    mock_simulator_controls.properties = _TEST_SIM_PROPERTIES
    mock_simulator_controls.set_seed = mock.Mock(
        sepc=AbstractSimulatorControls.set_seed, return_value=None
    )
    res = proxy_simulator_controls.set_seed(1)
    assert not res
    mock_simulator_controls.set_seed.assert_called_once_with(1)

    # Check that cache is empty after a new scenario is loaded
    assert not proxy_simulator_controls.sim_props


def test_upload_new_scenario():
    """Tests that ProxySimulatorControls implements upload_new_scenario"""
    pytest.xfail("Skip until we support GeoJSON scenarios")
