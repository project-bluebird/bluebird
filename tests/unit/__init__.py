"""
BlueBird unit test package
"""

from bluebird import settings
from bluebird.cache.base import EXTRAS

API_PREFIX = '/api/v' + str(settings.API_VERSION)

TEST_ACIDS = ['TST1001', 'TST1002']

# This is the same format as what BlueSky returns
TEST_DATA = {'id': TEST_ACIDS, 'alt': [1234, 5678], 'gs': [123.0, 456.0],
             'lat': [55.945336, 51.529877], 'lon': [-3.187299, -0.127720], 'vs': [4321, 8765]}

TEST_DATA_KEYS = list(TEST_DATA.keys()) + list(EXTRAS.keys())
TEST_DATA_KEYS.remove('id')
