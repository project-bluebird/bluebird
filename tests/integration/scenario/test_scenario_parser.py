
import pytest

import bluebird.scenario.scenario_parser as sp

from tests.integration import API_URL_BASE

import json
import requests
import jsonpath_rw_ext as jp

from os.path import abspath, join, exists

THIS_DIR = abspath(__file__)
ROOT_DIR = THIS_DIR.split("tests")[0]
SCENARIO_FILES_PATH = join(ROOT_DIR, "bluebird", "data", "scenarios")


@pytest.mark.parametrize(
    "sector_geojson,scenario_json",
    [("x_sector_hell.geojson","x_sector_hell_poisson_scenario.json")]
)
def test_scenario_parser(sector_geojson, scenario_json):
    """
    Tests the scenario parser creates a file that can be created in BlueSky.
    """
    with open(join(SCENARIO_FILES_PATH, sector_geojson)) as f:
        sector = f.read()
    with open(join(SCENARIO_FILES_PATH, scenario_json)) as f:
        scenario = f.read()

    SCENARIO_NAME = "x_sector_parsed_scenario"
    FILENAME = "{}.SCN".format(SCENARIO_NAME)

    generator = sp.ScenarioParser(sector, scenario)
    generator.write_bluesky_scenario(SCENARIO_NAME)

    assert exists(FILENAME), "Expected the scenario file to be created locally"

    content = [line.rstrip('\n') for line in open(FILENAME)]
    fixes = [
        x for x in jp.match("$..properties", json.loads(sector))
        if x["type"] == "FIX"
    ]
    aircraft = json.loads(scenario)['aircraft']

    assert sum("DEFWPT" in s for s in content) == len(fixes), "Unexpected number of DEFWPT statements in scenario file"
    assert sum("CRE" in s for s in content) == len(aircraft), "Unexpected number of CRE statements in scenario file"

    resp = requests.post(f"{API_URL_BASE}/reset")
    assert resp.status_code == 200, "Expected the sim to be reset"

    resp = requests.post(
        f"{API_URL_BASE}/scenario",
        json={"scn_name": SCENARIO_NAME, "content": content}
    )
    assert resp.status_code == 201, 'Expected the scenario to be created in BlueSky'
