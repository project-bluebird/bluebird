"""
BlueBird unit test package
"""

from bluebird import settings

API_PREFIX = '/api/v' + str(settings.API_VERSION)

TEST_ACIDS = ['TST1001', 'TST1002']

# This is the same format as what BlueSky returns
TEST_DATA = {'actype': ['B747', 'B747'], 'id': TEST_ACIDS, 'alt': [1234, 5678],
             'gs': [123.0, 456.0], 'lat': [55.94534, 51.52988], 'lon': [-3.18730, -0.12772],
             'vs': [4321, 8765]}

TEST_DATA_KEYS = list(TEST_DATA.keys())
TEST_DATA_KEYS.remove('id')

SIM_DATA = [0, 0, 123, '1970-01-01 00:00:00', len(TEST_ACIDS), 'TEST', 'TEST']
