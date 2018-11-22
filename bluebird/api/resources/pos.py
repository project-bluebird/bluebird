from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird as bb
from bluebird.utils import errprint


class Pos(Resource):
    """ BlueSky POS (position) command """

    def get(self, acid):
        # TODO Check acid valid

        errprint('POS {}'.format(acid))
        data = bb.STM_CACHE.getacdata(acid)

        if data is None:
            return 'No data'

        if '_validto' in data:
            del data['_validto']
        else:
            for item in data:
                del item['_validto']

        return jsonify(data)
