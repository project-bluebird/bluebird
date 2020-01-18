"""
Tests for the ProxySimulatorControls class
"""
# Todo check any missing methods
import datetime
import json
import logging
from io import StringIO

import mock
import pytest
from aviary.sector.sector_element import SectorElement

import bluebird.utils.properties as props
from bluebird.sim_proxy.proxy_aircraft_controls import ProxyAircraftControls
from bluebird.sim_proxy.proxy_simulator_controls import ProxySimulatorControls

# TODO(RKM 2020-01-02) We should be able to remove this import
from bluebird.utils.abstract_simulator_controls import (
    AbstractSimulatorControls,  # noreorder
)
from bluebird.utils.properties import Scenario
from bluebird.utils.properties import Sector
from bluebird.utils.properties import SimProperties
from tests.data import TEST_SCENARIO
from tests.data import TEST_SECTOR


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

_SECTOR_ELEMENT = SectorElement.deserialise(StringIO(json.dumps(TEST_SECTOR)))
_TEST_SECTOR = Sector(name="test-sector", element=_SECTOR_ELEMENT)

_TEST_SCENARIO = Scenario("test-scenario", content=TEST_SCENARIO)


def test_abstract_class_implemented():
    """Tests that ProxySimulatorControls implements the abstract base class"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    ProxySimulatorControls(mock_sim_controls, mock_aircraft_controls)


def test_properties():
    """Tests that ProxySimulatorControls implements properties"""

    in_agent_mode_patch = mock.patch(
        "bluebird.sim_proxy.proxy_simulator_controls.in_agent_mode"
    )
    in_agent_mode_patch.start()

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    properties_mock = mock.PropertyMock()
    properties_mock.return_value = _TEST_SIM_PROPERTIES
    type(mock_sim_controls).properties = properties_mock

    # Test call to _sim_controls.properties when not in agent mode

    in_agent_mode_patch.return_value = False

    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )
    props = proxy_simulator_controls.properties
    assert isinstance(props, SimProperties)
    assert props == _TEST_SIM_PROPERTIES
    properties_mock.assert_called_once()

    # Test call to _sim_controls.properties when in agent mode

    in_agent_mode_patch.return_value = True

    properties_mock.reset_mock()
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )
    props = proxy_simulator_controls.properties
    assert isinstance(props, SimProperties)
    assert props == _TEST_SIM_PROPERTIES
    properties_mock.assert_called_once()


def test_load_scenario():
    """Tests that ProxySimulatorControls implements properties"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test error handling from load_scenario

    mock_sim_controls.load_scenario.return_value = "Error"

    res = proxy_simulator_controls.load_scenario(_TEST_SCENARIO)
    assert res == "Error"

    # Test load_scenario

    mock_sim_controls.reset_mock()
    mock_sim_controls.load_scenario.return_value = None

    res = proxy_simulator_controls.load_scenario(_TEST_SCENARIO)
    assert not res
    mock_sim_controls.load_scenario.assert_called_once_with(_TEST_SCENARIO)


def test_start():
    """Tests that ProxySimulatorControls implements start"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test error handling from start
    mock_sim_controls.start = mock.Mock(
        sepc=AbstractSimulatorControls.start, return_value="Error"
    )
    res = proxy_simulator_controls.start()
    assert res == "Error"

    # Test valid response
    mock_sim_controls.start = mock.Mock(
        sepc=AbstractSimulatorControls.start, return_value=None
    )
    res = proxy_simulator_controls.start()
    assert not res


def test_reset():
    """Tests that ProxySimulatorControls implements reset"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test error handling from reset

    mock_sim_controls.reset = mock.Mock(
        sepc=AbstractSimulatorControls.reset, return_value="Error"
    )

    res = proxy_simulator_controls.reset()
    assert res == "Error"

    # Test valid response

    mock_sim_controls.properties = _TEST_SIM_PROPERTIES
    mock_sim_controls.reset = mock.Mock(
        sepc=AbstractSimulatorControls.reset, return_value=None
    )

    res = proxy_simulator_controls.reset()
    assert not res


def test_pause():
    """Tests that ProxySimulatorControls implements pause"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test error handling from pause
    mock_sim_controls.pause = mock.Mock(
        sepc=AbstractSimulatorControls.pause, return_value="Error"
    )
    res = proxy_simulator_controls.pause()
    assert res == "Error"

    # Test valid response
    mock_sim_controls.pause = mock.Mock(
        sepc=AbstractSimulatorControls.pause, return_value=None
    )
    res = proxy_simulator_controls.pause()
    assert not res


def test_resume():
    """Tests that ProxySimulatorControls implements resume"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test error handling from resume
    mock_sim_controls.resume = mock.Mock(
        sepc=AbstractSimulatorControls.resume, return_value="Error"
    )
    res = proxy_simulator_controls.resume()
    assert res == "Error"

    # Test valid response
    mock_sim_controls.resume = mock.Mock(
        sepc=AbstractSimulatorControls.resume, return_value=None
    )
    res = proxy_simulator_controls.resume()
    assert not res


def test_stop():
    """Tests that ProxySimulatorControls implements stop"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test error handling from stop
    mock_sim_controls.stop = mock.Mock(
        sepc=AbstractSimulatorControls.stop, return_value="Error"
    )
    res = proxy_simulator_controls.stop()
    assert res == "Error"

    # Test valid response
    mock_sim_controls.stop = mock.Mock(
        sepc=AbstractSimulatorControls.stop, return_value=None
    )
    res = proxy_simulator_controls.stop()
    assert not res


def test_step():
    """Tests that ProxySimulatorControls implements step"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test error handling from step
    mock_sim_controls.step = mock.Mock(
        sepc=AbstractSimulatorControls.step, return_value="Error"
    )
    res = proxy_simulator_controls.step()
    assert res == "Error"

    # Test valid response
    mock_sim_controls.properties = _TEST_SIM_PROPERTIES
    mock_sim_controls.step = mock.Mock(
        sepc=AbstractSimulatorControls.step, return_value=None
    )
    _mock_logger = mock.Mock(spec=logging.Logger)
    proxy_simulator_controls._logger = _mock_logger
    res = proxy_simulator_controls.step()
    assert not res


def test_set_speed():
    """Tests that ProxySimulatorControls implements set_speed"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test arg parsing
    with pytest.raises(AssertionError, match="Speed must be positive"):
        proxy_simulator_controls.set_speed(-1.0)

    # Test error handling from set_speed
    mock_sim_controls.set_speed = mock.Mock(
        sepc=AbstractSimulatorControls.set_speed, return_value="Error"
    )
    res = proxy_simulator_controls.set_speed(1.0)
    assert res == "Error"

    # Test set_speed
    mock_sim_controls.properties = _TEST_SIM_PROPERTIES
    mock_sim_controls.set_speed = mock.Mock(
        sepc=AbstractSimulatorControls.set_speed, return_value=None
    )
    res = proxy_simulator_controls.set_speed(1.0)
    assert not res
    mock_sim_controls.set_speed.assert_called_once_with(1.0)


def test_set_seed():
    """Tests that ProxySimulatorControls implements set_seed"""

    mock_sim_controls = mock.create_autospec(spec=AbstractSimulatorControls)
    mock_aircraft_controls = mock.create_autospec(spec=ProxyAircraftControls)
    proxy_simulator_controls = ProxySimulatorControls(
        mock_sim_controls, mock_aircraft_controls
    )

    # Test arg parsing

    with pytest.raises(AssertionError, match="Invalid seed"):
        proxy_simulator_controls.set_seed(-1)

    # Test error handling from set_seed

    mock_sim_controls.set_seed = mock.Mock(
        sepc=AbstractSimulatorControls.set_seed, return_value="Error"
    )
    res = proxy_simulator_controls.set_seed(1)
    assert res == "Error"

    # Test set_seed
    mock_sim_controls.properties = _TEST_SIM_PROPERTIES
    mock_sim_controls.set_seed = mock.Mock(
        sepc=AbstractSimulatorControls.set_seed, return_value=None
    )
    res = proxy_simulator_controls.set_seed(1)
    assert not res
    mock_sim_controls.set_seed.assert_called_once_with(1)
