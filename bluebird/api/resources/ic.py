from flask_restful import Resource

import bluebird as bb


class Ic(Resource):
    def get(self, filename='IC'):
        bb.CLIENT.send_stackcmd('IC ' + filename)

        # TODO Get return status
        return 'Ok?'
