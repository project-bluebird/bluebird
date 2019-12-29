"""
Package containing test files
"""

from pathlib import Path

_TEST_DATA_DIR = Path("tests/data")

TEST_EPISODE_LOG = _TEST_DATA_DIR / "test_episode.log"
assert TEST_EPISODE_LOG.exists(), f"Expected {TEST_EPISODE_LOG.absolute()} to exist"

TEST_SCENARIO = _TEST_DATA_DIR / "test_scenario.json"
assert TEST_SCENARIO.exists(), f"Expected {TEST_SCENARIO.absolute()} to exist"

TEST_SECTOR = _TEST_DATA_DIR / "test_sector.geojson"
assert TEST_SECTOR.exists(), f"Expected {TEST_SECTOR.absolute()} to exist"
