"""
Provides logic for the poissonScenario API endpoint
"""

import json
from aviary.sector.sector_element import SectorElement
from aviary.scenario.poisson_scenario import PoissonScenario as _PoissonScenario
from aviary.scenario.scenario_generator import ScenarioGenerator

from http import HTTPStatus
from flask_restful import Resource, reqparse

import bluebird.api.resources.utils.responses as responses
from bluebird.api.resources.utils.scenario_validation import validate_json_scenario
from bluebird.api.resources.utils.utils import sim_proxy, parse_args

_PARSER = reqparse.RequestParser()
_PARSER.add_argument("sector_type", type=str, location="args", required=True)
_PARSER.add_argument("scenario_params", type=dict, location="args", required=False)
_PARSER.add_argument("sector_params", type=dict, location="args", required=False)
_PARSER.add_argument("seed", type=int, location="args", required=False)

class PoissonScenario(Resource):
    """Contains logic for the PoissonScenario endpoint"""

    @staticmethod
    def post():
        """Logic for POST events"""

        req_args = parse_args(_PARSER)

        sector_type = req_args["sector_type"]
        sector_params = req_args["sector_params"]
        scn_params = req_args["scenario_params"]
        seed = req_args["seed"]

        if not sector_type:
            return responses.bad_request_resp("Sector type must be provided")

        sector = SectorElement(shape=sector_type)
        algorithm = _PoissonScenario(arrival_rate=2/60, sector_element=sector, seed=seed)
        scen_gen = ScenarioGenerator(scenario_algorithm=algorithm)
        scenario = scen_gen.generate_scenario(duration=600)
        content = json.loads(json.dumps(scenario))

        err = validate_json_scenario(content)
        if err:
            return responses.bad_request_resp(f"Invalid scenario content: {err}")

        # TODO: pic a scn_name other than "test"
        err = sim_proxy().simulation.upload_new_scenario("test", content)

        return responses.checked_resp(err, HTTPStatus.CREATED)
