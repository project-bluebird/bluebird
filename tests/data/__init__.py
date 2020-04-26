"""
Package containing test files
"""
# NOTE(rkm 2020-01-18) We tag the data files with their source commit from Aviary. This
# helps when debugging, however we have to manually remove them here
import json
from pathlib import Path

_TEST_DATA_DIR = Path("tests/data")

TEST_EPISODE_LOG_FILE = _TEST_DATA_DIR / "test_episode.log"
with open(TEST_EPISODE_LOG_FILE) as f:
    TEST_EPISODE_LOG = list(line.rstrip("\n") for line in f)

_TEST_SCENARIO_FILE = _TEST_DATA_DIR / "test_scenario.json"
with open(_TEST_SCENARIO_FILE) as f:
    TEST_SCENARIO = json.load(f)
    TEST_SCENARIO.pop("_source", None)

_TEST_SECTOR_FILE = _TEST_DATA_DIR / "test_sector.geojson"
with open(_TEST_SECTOR_FILE) as f:
    TEST_SECTOR = json.load(f)
    TEST_SECTOR.pop("_source", None)
