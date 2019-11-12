"""
Package for integration tests
"""

from bluebird.settings import Settings

API_URL_BASE = "http://localhost:5001/api/v" + str(Settings.API_VERSION)
