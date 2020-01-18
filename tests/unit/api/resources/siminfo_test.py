"""
Tests for the SIMINFO endpoint
"""
from http import HTTPStatus

import mock

from bluebird.settings import Settings
from bluebird.utils.types import Callsign
from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path
from tests.unit.api.resources import TEST_SIM_PROPS


_ENDPOINT = "siminfo"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_siminfo_get(test_flask_client):
    """Tests the POST method"""

    with mock.patch(patch_utils_path(_ENDPOINT)) as utils_patch:

        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from simulation properties

        sim_proxy_mock.simulation.properties = "Error"

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't get the sim properties: Error"

        # Test error from aircraft callsigns

        sim_proxy_mock.simulation.properties = TEST_SIM_PROPS
        sim_proxy_mock.aircraft.callsigns = "Error"

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't get the callsigns: Error"

        # Test valid response

        sim_proxy_mock.aircraft.callsigns = [Callsign("AAA"), Callsign("BBB")]

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {
            "callsigns": ["AAA", "BBB"],
            "mode": Settings.SIM_MODE.name,
            "sector_name": TEST_SIM_PROPS.sector_name,
            "scenario_name": TEST_SIM_PROPS.scenario_name,
            "scenario_time": 0,
            "seed": 0,
            "sim_type": "BlueSky",
            "speed": 1.0,
            "state": "INIT",
            "dt": TEST_SIM_PROPS.dt,
            "utc_datetime": str(TEST_SIM_PROPS.utc_datetime),
        }
