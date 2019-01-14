"""
Serves the repositories README.md file as the default index page
"""

import os

import markdown


def readme(root_path):
	"""
	Serves README.md

	:return: HTML string of the repositories README.md file
	"""

	with open(os.path.dirname(root_path) + '/../README.md', 'r') as readme_md:
		return markdown.markdown(readme_md.read())
