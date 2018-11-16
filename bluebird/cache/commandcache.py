import sys

from bluebird.cache.utils import *


class CommandCache(object):

    def __init__(self):
        self.data = {}

    def get(self, command, args):
        # TODO Check valid command
        combined = command + ' ' + args

        if combined in self.data and before(self.data[combined][1] + default_lifetime):
            print('Cache hit', file=sys.stderr)
            return self.data[combined][0]

        print('Cache miss', file=sys.stderr)

        # TODO Call the command
        data = 'hey!'

        self.data[combined] = [data, now()]
        return data
