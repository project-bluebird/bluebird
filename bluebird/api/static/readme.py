import os

import markdown

import bluebird as bb


def index():
    """ Serves README.md """
    with open(os.path.dirname(bb.APP.root_path) + '/../README.md', 'r') as readme_md:
        return markdown.markdown(readme_md.read())
