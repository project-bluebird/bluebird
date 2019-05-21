"""

"""

import logging

from flask_restful import Resource, reqparse

from bluebird.api.resources.utils import process_stack_cmd

import bluebird.client as bb_client
from bluebird.cache import AC_DATA

import time

PARSER = reqparse.RequestParser()
PARSER.add_argument('t_diff', type=int, location='json', required=True)

_LOGGER = logging.getLogger('bluebird')

class Step(Resource):
    """
    Contains logic for the step endpoint
    """

    @staticmethod
    def post():
        """
    	Logic for POST events.
    	:return: :class:`~flask.Response`
        """

        parsed = PARSER.parse_args()
        t_diff = parsed['t_diff']

        resp = process_stack_cmd('HOLD')
        if resp.status_code != 200:
            return resp

        dt_mult = min(t_diff, 10)
        t_steps = t_diff/dt_mult

        cmd = f'DTMULT {dt_mult}'
        err = bb_client.CLIENT_SIM.send_stack_cmd(cmd)

        if not err:
        	AC_DATA.set_log_rate(dt_mult)

        t = time.time()
        resp = process_stack_cmd('OP')

        if resp.status_code != 200:
            return resp

        t1 = time.time() - t
        t = time.time()
        _LOGGER.info(f'time for OP command {time.strftime("%H:%M:%S", time.gmtime(t1))}')

        time.sleep(t_diff)

        t2 = time.time() - t
        t = time.time()
        _LOGGER.info(f't_steps {t_steps}')
        _LOGGER.info(f'time to wait t_steps {time.strftime("%H:%M:%S", time.gmtime(t2))}')

        resp = process_stack_cmd('HOLD')


        t3 = time.time() - t
        _LOGGER.info(f'time to send hold command {time.strftime("%H:%M:%S", time.gmtime(t3))}')

        return resp
