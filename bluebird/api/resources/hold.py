"""
Provides logic for the HOLD (simulation pause) API endpoint
"""

from flask_restful import Resource

from bluebird.api.resources.utils import process_stack_cmd


class Hold(Resource):
    """
    BlueSky HOLD (simulation pause) command
    """

    @staticmethod
    def post():
        """
        POST the HOLD command and process the response.
        :return: :class:`~flask.Response`
        """

        return process_stack_cmd("HOLD")
