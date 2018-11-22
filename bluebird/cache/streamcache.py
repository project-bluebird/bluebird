from bluebird.cache.utils import *


class StreamCache(object):
    """ Holds the most recent state of the simulation """

    def __init__(self):
        self.acdata = {}

    def getacdata(self, acid):

        if acid == 'ALL':
            return self.acdata

        if acid in self.acdata and before(self.acdata[acid]['_validto'] + default_lifetime):
            return dict(self.acdata[acid])

        # TODO Handle missing aircraft data
        return

    def fill(self, data):

        if isinstance(data, dict) and 'id' in data:

            # Can definitely tidy this up a bit
            for i in range(len(data['id'])):
                acid = data['id'][i]
                self.acdata[acid] = {
                    'alt': data['alt'][i],
                    'lat': data['lat'][i],
                    'lon': data['lon'][i],
                    'gs': data['gs'][i],
                    'vs': data['vs'][i],
                    '_validto': now()
                }

    # TODO Call this when sim reset
    def clear(self):
        self.acdata = {}
