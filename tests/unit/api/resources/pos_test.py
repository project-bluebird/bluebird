"""
Tests for the POS endpoint
"""

from http import HTTPStatus

import mock

import bluebird.api as api
import bluebird.api.resources.utils.utils as utils
from bluebird.api.resources.utils.responses import bad_request_resp

from tests.unit.api.resources import endpoint_path
from tests.unit.api.resources import patch_utils_path
from tests.unit.api.resources import TEST_AIRCRAFT_PROPS
from tests.unit.api.resources import TEST_SIM_PROPS


_ENDPOINT = "pos"
_ENDPOINT_PATH = endpoint_path(_ENDPOINT)


def test_pos_get_single(test_flask_client):
    """Tests the GET method with a single aircraft"""

    # Test arg parsing

    endpoint_str = f"{_ENDPOINT_PATH}?{utils.CALLSIGN_LABEL}"

    callsign = ""
    resp = test_flask_client.get(f"{endpoint_str}={callsign}")
    assert resp.status_code == HTTPStatus.BAD_REQUEST
    assert utils.CALLSIGN_LABEL in resp.json["message"]

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL
        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from simulation properties

        sim_proxy_mock.simulation.properties = "Error"

        endpoint_str = f"{endpoint_str}=TEST"

        resp = test_flask_client.get(endpoint_str)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Error"

        # Test aircraft existence check

        sim_proxy_mock.simulation.properties = TEST_SIM_PROPS

        with api.FLASK_APP.test_request_context():
            utils_patch.check_exists.return_value = bad_request_resp("Missing aircraft")

        resp = test_flask_client.get(endpoint_str)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "Missing aircraft"

        # Test error from aircraft properties

        utils_patch.check_exists.return_value = None
        sim_proxy_mock.aircraft.properties.return_value = "Missing properties"

        resp = test_flask_client.get(endpoint_str)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Missing properties"

        # Test valid response

        sim_proxy_mock.aircraft.properties.return_value = TEST_AIRCRAFT_PROPS

        resp = test_flask_client.get(endpoint_str)
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {
            **utils.convert_aircraft_props(TEST_AIRCRAFT_PROPS),
            "scenario_time": TEST_SIM_PROPS.scenario_time,
        }


def test_pos_get_all(test_flask_client):
    """Tests the GET method with all aircraft"""

    with mock.patch(patch_utils_path(_ENDPOINT), wraps=utils) as utils_patch:

        utils_patch.CALLSIGN_LABEL = utils.CALLSIGN_LABEL
        sim_proxy_mock = mock.Mock()
        utils_patch.sim_proxy.return_value = sim_proxy_mock

        # Test error from all_properties

        sim_proxy_mock.simulation.properties = TEST_SIM_PROPS
        sim_proxy_mock.aircraft.all_properties = "Error"

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.INTERNAL_SERVER_ERROR
        assert resp.data.decode() == "Couldn't get the aircraft properties: Error"

        # Test error when no aircraft

        sim_proxy_mock.aircraft.all_properties = None

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.BAD_REQUEST
        assert resp.data.decode() == "No aircraft in the simulation"

        # Test valid response

        sim_proxy_mock.aircraft.all_properties = {
            str(TEST_AIRCRAFT_PROPS.callsign): TEST_AIRCRAFT_PROPS,
        }

        resp = test_flask_client.get(_ENDPOINT_PATH)
        assert resp.status_code == HTTPStatus.OK
        assert resp.json == {
            **utils.convert_aircraft_props(TEST_AIRCRAFT_PROPS),
            **{"scenario_time": TEST_SIM_PROPS.scenario_time},
        }
