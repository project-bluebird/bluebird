from bluebird.cache.utils import *


class StreamCache(object):
    def __init__(self):
        self.data = {}

    def getacdata(self, acid):

        if acid in self.data and before(self.data[acid]['_validto'] + default_lifetime):
            return dict(self.data[acid])

        # TODO Handle missing aircraft data
        return

    def fill(self, data):

        if isinstance(data, dict) and 'id' in data:

            # Can definitely tidy this up a bit
            for i in range(len(data['id'])):
                acid = data['id'][i]
                self.data[acid] = {
                    'alt': data['alt'][i],
                    'lat': data['lat'][i],
                    'lon': data['lon'][i],
                    'gs': data['gs'][i],
                    'vs': data['vs'][i],
                    '_validto': now()
                }

                # errprint(self.data[acid])

    # TODO Call this when sim reset
    def clear(self):
        self.data = {}
