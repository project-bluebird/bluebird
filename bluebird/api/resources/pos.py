from flask import jsonify
from flask_restful import Resource

import bluebird as bb


class Pos(Resource):
    """ BlueSky POS (position) command """

    def get(self, acid):
        data = bb.STM_CACHE.getacdata(acid)

        if data is None:
            return 'No data', 404

        resp = jsonify(data)
        resp.status_code = 200
        return resp
