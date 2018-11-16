import os

import markdown
from flask import Flask
from flask_restful import Api

from bluebird import settings


class BlueBirdApi(Api):
    def __init__(self, *args, **kwargs):
        print('BlueBirdApi init')
        super(BlueBirdApi, self).__init__(*args, **kwargs)


app = Flask(__name__)
api = BlueBirdApi(app, prefix='/api/v' + str(settings.API_VERSION))

# region Resources

from .resources import Pos
from .resources import Ic

api.add_resource(Pos, '/pos/<acid>')
api.add_resource(Ic, '/ic/<filename>')


# endregion

# region Static routes

def index():
    """ Serves README.md """
    with open(os.path.dirname(app.root_path) + '/../README.md', 'r') as readme_md:
        return markdown.markdown(readme_md.read())


app.add_url_rule('/', 'index', index)

# endregion
