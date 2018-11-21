from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird as bb
from bluebird.utils import errprint


class Pos(Resource):
    def get(self, acid):
        # TODO Check acid valid
        # TODO Handle timeouts

        errprint('POS {}'.format(acid))
        data = bb.STM_CACHE.getacdata(acid)

        if data is None:
            return 'No data'

        del data['_validto']

        return jsonify(data)


parser = reqparse.RequestParser()
parser.add_argument('pos')
