from flask_restful import Resource

import bluebird


class Ic(Resource):
    def get(self, filename='IC'):
        bluebird.CLIENT.send_stackcmd('IC ' + filename)

        # TODO Get return status
        return 'Ok?'
