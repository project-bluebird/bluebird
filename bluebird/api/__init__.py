"""
Contains logic for flask and our app routes
"""

import logging

from flask import Flask, request
from flask_cors import CORS
from flask_restful import Api

from bluebird import settings
from . import resources as res, static


class BlueBirdApi(Api):
	"""
	Subclass of the Flask API object - allows us to customise it later if needed
	"""

	def __init__(self, *args, **kwargs):
		super(BlueBirdApi, self).__init__(*args, **kwargs)


# Create the Flask app & API, with the given prefix
FLASK_APP = Flask(__name__)
CORS(FLASK_APP)
FLASK_API = BlueBirdApi(FLASK_APP, prefix='/api/v' + str(settings.API_VERSION))

# Add hooks to log request response data

LOGGER = logging.getLogger(__name__)


@FLASK_APP.before_request
def before_req():
	"""
	Method called before every request is handled
	:return:
	"""

	json = request.get_json()
	LOGGER.info(f'REQ: {request.method} {request.full_path} "{json if json else ""}"')


@FLASK_APP.after_request
def after_req(response):
	"""
	Method called before any response is returned
	:param response:
	:return:
	"""

	json = response.get_json()

	if 'eplog' in request.url.lower():
		json = 'EPLOG data'

	LOGGER.info(f'RESP: {response.status_code} "{json if json else ""}"')

	return response


# Our API endpoints are defined below here

# region Resources

# Aircraft control
FLASK_API.add_resource(res.AddWpt, '/addwpt')
FLASK_API.add_resource(res.Alt, '/alt')
FLASK_API.add_resource(res.Cre, '/cre')
FLASK_API.add_resource(res.Direct, '/direct')
FLASK_API.add_resource(res.Hdg, '/hdg')
FLASK_API.add_resource(res.ListRoute, '/listroute')
FLASK_API.add_resource(res.Pos, '/pos')
FLASK_API.add_resource(res.Spd, '/spd')
FLASK_API.add_resource(res.Vs, '/vs')

# Simulation control
FLASK_API.add_resource(res.DefWpt, '/defwpt')
FLASK_API.add_resource(res.DtMult, '/dtmult')
FLASK_API.add_resource(res.Hold, '/hold')
FLASK_API.add_resource(res.Ic, '/ic')
FLASK_API.add_resource(res.Op, '/op')
FLASK_API.add_resource(res.Reset, '/reset')
FLASK_API.add_resource(res.Scenario, '/scenario')
FLASK_API.add_resource(res.Step, '/step')
FLASK_API.add_resource(res.Time, '/time')

# Application control
# FLASK_API.add_resource(res.EpInfo, '/epinfo')
FLASK_API.add_resource(res.EpLog, '/eplog')
FLASK_API.add_resource(res.Shutdown, '/shutdown')

# endregion

# region Static routes

FLASK_APP.add_url_rule('/', 'index', static.readme, defaults={'root_path': FLASK_APP.root_path})

# endregion
