from flask import jsonify
from flask_restful import Resource, reqparse

import bluebird as bb
from bluebird.utils.strings import is_acid

parser = reqparse.RequestParser()
parser.add_argument('acid', type=str, location='json', required=True)
parser.add_argument('alt', type=str, location='json', required=True)
parser.add_argument('vspd', type=str, location='json', required=False)


class Alt(Resource):
    """ BlueSky CRE (create aircraft) command """

    def post(self):

        args = parser.parse_args()

        acid = args['acid']

        if not is_acid(acid):
            resp = jsonify('Invalid ACID \'{}\''.format(acid))
            resp.status_code = 400
            return resp

        if 'acdata' in bb.CACHES and bb.CACHES['acdata'].get(acid) is None:
            resp = jsonify('AC {} not found'.format(acid))
            resp.status_code = 404
            return resp

        cmd = 'ALT {acid} {alt} '.format(**args)

        if args['vspd'] is not None:
            cmd += args['vspd']

        bb.CLIENT.send_stackcmd(cmd)

        resp = jsonify('Ok?')
        resp.status_code = 418
        return resp
