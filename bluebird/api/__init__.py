"""
Contains logic for flask and our app routes
"""

from flask import Flask
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
FLASK_API = BlueBirdApi(FLASK_APP, prefix='/api/v' + str(settings.API_VERSION))

# Our API endpoints are defined below here

# region Resources

# TODO Parser inheritance for common arguments
# See: https://flask-restful.readthedocs.io/en/0.3.5/reqparse.html#parser-inheritance
# TODO Input sanitisation for all endpoints
# TODO Allow units to be specified

FLASK_API.add_resource(res.Pos, '/pos/<acid>')
FLASK_API.add_resource(res.Ic, '/ic')
FLASK_API.add_resource(res.Cre, '/cre')
FLASK_API.add_resource(res.Alt, '/alt')

# endregion

# region Static routes

FLASK_APP.add_url_rule('/', 'index', static.readme, defaults={'root_path': FLASK_APP.root_path})

# endregion
