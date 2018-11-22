from flask_restful import Resource

import bluebird as bb


class Ic(Resource):
    """ BlueSky IC (initial condition) command """

    def get(self, filename='IC'):
        bb.CLIENT.send_stackcmd('IC ' + filename)

        # TODO Get return status. Can hook this up to a 'SIMRESET' signal?
        return 'Ok?'
