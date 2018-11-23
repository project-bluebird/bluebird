from bluebird.utils.timeutils import now

from .cache import Cache


# TODO Call clear when sim reset
class AcDataCache(Cache):
    """ Holds the most recent aircraft data """

    def __init__(self, *args, **kwargs):
        super(AcDataCache, self).__init__(*args, **kwargs)

    def get(self, acid):

        # If requested, just return the complete acdata
        if acid.upper() == 'ALL':
            return self.store

        return super(AcDataCache, self).get(acid)

    def fill(self, data):

        if isinstance(data, dict) and 'id' in data:

            # TODO Can definitely tidy this up
            for i in range(len(data['id'])):
                acid = data['id'][i]
                self.store[acid] = {
                    'alt': data['alt'][i],
                    'lat': data['lat'][i],
                    'lon': data['lon'][i],
                    'gs': data['gs'][i],
                    'vs': data['vs'][i],
                    '_validto': now()
                }
