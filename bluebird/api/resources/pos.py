from flask import jsonify
from flask_restful import Resource

import bluebird as bb
from bluebird.utils import errprint


class Pos(Resource):
    def get(self, acid):
        # TODO Check acid valid
        # TODO Handle timeouts

        acid = acid.upper()
        errprint('POS {}'.format(acid))

        data = bb.STM_CACHE.getacdata(acid)

        if data is None:
            return 'No data'

        # TODO Remove nested keys if we are returning all AC data
        if '_validto' in data:
            del data['_validto']
        else:
            for item in data:
                del item['_validto']

        return jsonify(data)

# TODO Check if this is needed
# parser = reqparse.RequestParser()
# parser.add_argument('pos')
