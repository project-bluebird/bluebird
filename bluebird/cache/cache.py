from bluebird.utils.timeutils import before, default_lifetime, now

VALID_TO = '_validTo'


class Cache(object):
    """ Simple cache implementation. Holds data streamed from the simulation. """

    def __init__(self, *args, **kwargs):
        self.store = {}

    def get(self, key):

        if key in self.store and before(self.store[key][VALID_TO] + default_lifetime):
            return dict(self.store[key])

        return self.miss(key)

    def fill(self, data):

        if not isinstance(data, dict):
            raise TypeError("Unsupported data type for cache: {}".format(type(data)))

        for key in data:
            item = data[key]
            if isinstance(item, dict):
                self.store[key] = {k: v for k, v in item}
                self.store[key][VALID_TO] = now()

    def miss(self, key):
        return None

    def clear(self):
        self.store = {}
