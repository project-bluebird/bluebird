"""
Contains logic for flask and our app routes
"""

from flask import Flask
from flask_restful import Api
from flask_cors import CORS

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

# Our API endpoints are defined below here

# region Resources

# Aircraft control
FLASK_API.add_resource(res.Alt, '/alt')
FLASK_API.add_resource(res.Cre, '/cre')
FLASK_API.add_resource(res.Hdg, '/hdg')
FLASK_API.add_resource(res.Pos, '/pos')
FLASK_API.add_resource(res.Spd, '/spd')
FLASK_API.add_resource(res.Vs, '/vs')

# Simulation control
FLASK_API.add_resource(res.Hold, '/hold')
FLASK_API.add_resource(res.Ic, '/ic')
FLASK_API.add_resource(res.Op, '/op')

# endregion

# region Static routes

FLASK_APP.add_url_rule('/', 'index', static.readme, defaults={'root_path': FLASK_APP.root_path})

# endregion
