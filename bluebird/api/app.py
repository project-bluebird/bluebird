from flask import Flask
from flask_restful import Api

import bluebird.api.resources as res
import bluebird.api.static as static
from bluebird import settings


# Subclass of the API object - allows us to customise it later if needed
class BlueBirdApi(Api):
    def __init__(self, *args, **kwargs):
        super(BlueBirdApi, self).__init__(*args, **kwargs)


# Create the Flask app & API, with the given prefix
app = Flask(__name__)
api = BlueBirdApi(app, prefix='/api/v' + str(settings.API_VERSION))

# Our API endpoints are defined below here

# region Resources

api.add_resource(res.Pos, '/pos/<acid>')
api.add_resource(res.Ic, '/ic')
api.add_resource(res.Cre, '/cre')

# endregion

# region Static routes

app.add_url_rule('/', 'index', static.index)

# endregion
