"""
BlueBird test package
"""

from dotenv import load_dotenv

from bluebird.settings import Settings


API_PREFIX = "/api/v" + str(Settings.API_VERSION)

load_dotenv(verbose=True, override=True)
