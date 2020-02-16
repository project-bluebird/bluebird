"""
Simple test script for the MachColl metrics
"""
import json
from pathlib import Path

import requests


def main():

    test_sector_path = Path("tests", "data", "test_sector.geojson")
    with open(test_sector_path) as f:
        test_sector_content = json.load(f)
    test_sector_content.pop("_source", None)

    test_scenario_path = Path("tests", "data", "test_scenario.json")
    with open(test_scenario_path) as f:
        test_scenario_content = json.load(f)
    test_scenario_content.pop("_source", None)

    api_base = "http://0.0.0.0:5001/api/v2"

    get_sim_info = ["get", "siminfo", "", {}]
    request_list = [
        ["post", "reset", "", {}],
        get_sim_info,
        ["post", "sector", "", {"name": "test_sector", "content": test_sector_content}],
        get_sim_info,
        [
            "post",
            "scenario",
            "",
            {"name": "test_scenario", "content": test_scenario_content},
        ],
        get_sim_info,
        ["post", "step", "", {}],
        ["get", "metric", "provider=machcoll&name=metrics.score", {}],
    ]

    for request in request_list:
        input(
            f"Next request is: {request[0]} {api_base}/{request[1]}?{request[2]}"
            f" {request[3]}\nEnter to send!"
        )
        resp = getattr(requests, request[0])(
            f"{api_base}/{request[1]}?{request[2]}", json=request[3]
        )
        print("RESP:")
        try:
            print(json.dumps(resp.json(), indent=4, sort_keys=True))
        except json.decoder.JSONDecodeError:
            print(f"'{resp.text}'")
        print()
        if not resp.ok:
            print("Exiting on error")
            return 1

    return 0


if __name__ == "__main__":
    exit(main())
