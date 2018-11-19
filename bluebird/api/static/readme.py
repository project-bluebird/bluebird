
def index():
    """ Serves README.md """
    with open(os.path.dirname(app.root_path) + '/../README.md', 'r') as readme_md:
        return markdown.markdown(readme_md.read())


