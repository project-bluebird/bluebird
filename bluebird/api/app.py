from flask import Flask
from flask_restful import Api

import bluebird.api.resources as res
import bluebird.api.static as static
from bluebird import settings


class BlueBirdApi(Api):
    def __init__(self, *args, **kwargs):
        print('BlueBirdApi init')
        super(BlueBirdApi, self).__init__(*args, **kwargs)


app = Flask(__name__)
api = BlueBirdApi(app, prefix='/api/v' + str(settings.API_VERSION))

# region Resources

api.add_resource(res.Pos, '/pos/<acid>')
api.add_resource(res.Ic, '/ic/<filename>')

# endregion

# region Static routes

app.add_url_rule('/', 'index', static.index)

# endregion
