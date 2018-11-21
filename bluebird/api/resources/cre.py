from flask_restful import Resource, reqparse

import bluebird as bb
from bluebird.utils.errprint import errprint

# TODO Tidy this (can we define as a dict?)
parser = reqparse.RequestParser()
parser.add_argument('acid', type=str, location='json', required=True)
parser.add_argument('type', type=str, location='json', required=True)
parser.add_argument('lat', type=str, location='json', required=True)
parser.add_argument('lon', type=str, location='json', required=True)
parser.add_argument('hdg', type=str, location='json', required=True)
parser.add_argument('alt', type=str, location='json', required=True)
parser.add_argument('spd', type=str, location='json', required=True)


# Example JSON:
# {
# 	"acid": "test1234",
# 	"type": "B744",
# 	"lat": "0",
# 	"lon": "0",
# 	"hdg": "0",
# 	"alt": "FL250",
# 	"spd": "250"
# }

class Cre(Resource):

    def post(self):
        args = parser.parse_args()
        cmd = 'CRE {acid} {type} {lat} {lon} {hdg} {alt} {spd}'.format(**args)
        errprint(cmd)

        bb.CLIENT.send_stackcmd(cmd)
