"""
Tests for BlueSkySimulatorControls
"""

import json
from datetime import datetime

import mock

from bluebird.sim_client.bluesky.bluesky_simulator_controls import (
    BlueSkySimulatorControls,
)
from bluebird.utils.properties import Scenario
from bluebird.utils.properties import Sector
from bluebird.utils.properties import SimProperties
from bluebird.utils.properties import SimState

from tests.data import TEST_SCENARIO


_TEST_SIMINFO = [
    1.54,  # Sim speed
    0.05,  # Sim dt
    1234,  # Sim time (seconds elapsed)
    "2020-01-02 12:34:56",  # Sim time (UTC datetime)
    4,  # Number of aircraft
    2,  # Sim state
    "test-scenario",  # Current scenario name
]

with open(TEST_SCENARIO, "r") as f:
    _TEST_SCENARIO = Scenario(name="test-scenario", content=json.load(f))


def test_abstract_class_implemented():
    """Tests that BlueSkyAircraftControls implements the abstract base class"""

    bs_client_mock = mock.Mock()
    BlueSkySimulatorControls(bs_client_mock)


def test_properties():
    """Test the properties property"""

    bs_client_mock = mock.Mock()
    bs_client_mock.sim_info_stream_data = _TEST_SIMINFO
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    with mock.patch(
        "bluebird.sim_client.bluesky.bluesky_simulator_controls.in_agent_mode"
    ) as in_agent_mode_mock:
        in_agent_mode_mock.return_value = False
        props = bs_sim_controls.properties

    assert isinstance(props, SimProperties)
    assert props == SimProperties(
        sector_name=None,
        scenario_name="test-scenario",
        scenario_time=1234,
        seed=None,
        speed=1.54,
        state=SimState.RUN,
        dt=0.05,
        utc_datetime=datetime(2020, 1, 2, 12, 34, 56),
    )


def test_load_scenario():
    """Test load_scenario"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    # Test load existing scenario - error response

    bs_client_mock.load_scenario.return_value = "Error"
    existing_scenario = Scenario("TEST", [])
    err = bs_sim_controls.load_scenario(existing_scenario)
    assert err == "Error"

    # Test load existing scenario - valid response

    bs_client_mock.reset_mock()
    bs_client_mock.load_scenario.return_value = None
    err = bs_sim_controls.load_scenario(existing_scenario)
    assert not err
    bs_client_mock.load_scenario.assert_called_once_with("test.scn", True)

    with mock.patch(
        "bluebird.sim_client.bluesky.bluesky_simulator_controls.BlueskyParser"
    ) as bs_parser_patch:

        # Test uploading new scenario - error from BlueSkyParser

        bs_parser_patch.side_effect = Exception()
        bs_sim_controls.load_sector(Sector("unused", True))

        err = bs_sim_controls.load_scenario(_TEST_SCENARIO)
        assert err.startswith("Could not parse a BlueSky scenario")

        # Test uploading new scenario - error from upload_new_scenario

        bs_parser_patch.side_effect = None
        bs_client_mock.upload_new_scenario.return_value = "Error"

        err = bs_sim_controls.load_scenario(_TEST_SCENARIO)
        assert err == "Error"

        # Test uploading new scenario - valid response

        bs_client_mock.upload_new_scenario.return_value = None

        err = bs_sim_controls.load_scenario(_TEST_SCENARIO)
        assert not err


def test_start():
    """Test start"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    bs_client_mock.send_stack_cmd.return_value = "Error"
    err = bs_sim_controls.start()
    assert err == "Error"

    bs_client_mock.reset_mock()
    bs_client_mock.send_stack_cmd.return_value = None
    err = bs_sim_controls.start()
    assert not err
    bs_client_mock.send_stack_cmd.assert_called_once_with("OP")


def test_reset():
    """Test reset"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    bs_client_mock.reset_sim.return_value = "Error"
    err = bs_sim_controls.reset()
    assert err == "Error"

    bs_client_mock.reset_mock()
    bs_client_mock.reset_sim.return_value = None
    err = bs_sim_controls.reset()
    assert not err
    bs_client_mock.reset_sim.assert_called_once()


def test_pause():
    """Test pause"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    bs_client_mock.send_stack_cmd.return_value = "Error"
    err = bs_sim_controls.pause()
    assert err == "Error"

    bs_client_mock.reset_mock()
    bs_client_mock.send_stack_cmd.return_value = None
    err = bs_sim_controls.pause()
    assert not err
    bs_client_mock.send_stack_cmd.assert_called_once_with("HOLD")


def test_resume():
    """Test resume"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    bs_client_mock.send_stack_cmd.return_value = "Error"
    err = bs_sim_controls.resume()
    assert err == "Error"

    bs_client_mock.reset_mock()
    bs_client_mock.send_stack_cmd.return_value = None
    err = bs_sim_controls.resume()
    assert not err
    bs_client_mock.send_stack_cmd.assert_called_once_with("OP")


def test_stop():
    """Test stop"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    bs_client_mock.send_stack_cmd.return_value = "Error"
    err = bs_sim_controls.stop()
    assert err == "Error"

    bs_client_mock.reset_mock()
    bs_client_mock.send_stack_cmd.return_value = None
    err = bs_sim_controls.stop()
    assert not err
    bs_client_mock.send_stack_cmd.assert_called_once_with("STOP")


def test_step():
    """Test step"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    bs_client_mock.step.return_value = "Error"
    err = bs_sim_controls.step()
    assert err == "Error"

    bs_client_mock.reset_mock()
    bs_client_mock.step.return_value = None
    err = bs_sim_controls.step()
    assert not err
    bs_client_mock.step.assert_called_once()


def test_set_speed():
    """Test set_speed"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    bs_client_mock.send_stack_cmd.return_value = "Error"
    err = bs_sim_controls.set_speed(1.23)
    assert err == 'No confirmation received from BlueSky. Received: "Error"'

    bs_client_mock.reset_mock()
    dt_mult = 10.1
    bs_client_mock.send_stack_cmd.return_value = [f"Speed set to {dt_mult}"]
    err = bs_sim_controls.set_speed(dt_mult)
    assert not err
    bs_client_mock.send_stack_cmd.assert_called_once_with(
        f"DTMULT {dt_mult}", response_expected=True
    )


def test_set_seed():
    """Test set_seed"""

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    bs_client_mock.send_stack_cmd.return_value = "Error"
    err = bs_sim_controls.set_seed(0)
    assert err == 'No confirmation received from BlueSky. Received: "Error"'

    bs_client_mock.reset_mock()
    seed = 4444
    bs_client_mock.send_stack_cmd.return_value = [f"Seed set to {seed}"]
    err = bs_sim_controls.set_seed(seed)
    assert not err
    bs_client_mock.send_stack_cmd.assert_called_once_with(
        f"SEED {seed}", response_expected=True
    )


def test_dt_mult_handling():
    """
    Tests that we properly track the dtmult value. BlueSky resets this value to 1 after
    a reset. We can't query for the current value however, so have to track it ourselves
    """

    bs_client_mock = mock.Mock()
    bs_sim_controls = BlueSkySimulatorControls(bs_client_mock)

    dt_mult = 4
    bs_client_mock.send_stack_cmd.return_value = [f"Speed set to {dt_mult}"]
    err = bs_sim_controls.set_speed(dt_mult)
    assert not err

    bs_client_mock.sim_info_stream_data = _TEST_SIMINFO

    with mock.patch(
        "bluebird.sim_client.bluesky.bluesky_simulator_controls.in_agent_mode"
    ) as in_agent_mode_mock:

        in_agent_mode_mock.return_value = True

        props = bs_sim_controls.properties
        assert isinstance(props, SimProperties)
        assert props.speed == dt_mult

        bs_client_mock.reset_sim.return_value = None
        err = bs_sim_controls.reset()
        assert not err

        props = bs_sim_controls.properties
        assert isinstance(props, SimProperties)
        assert props.speed == 1
