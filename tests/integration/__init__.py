"""
Package for integration tests
"""

from bluebird.settings import Settings

API_URL_BASE = f"http://localhost:{Settings.PORT}/api/v{Settings.API_VERSION}"
