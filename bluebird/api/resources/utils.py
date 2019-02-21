"""
Contains utility functions for the API resources
"""

from flask import jsonify
from flask_restful import reqparse

import bluebird.client
from bluebird.cache import AC_DATA
from bluebird.utils.debug import errprint
from bluebird.utils.strings import is_acid


def generate_arg_parser(_req_args, opt_args=None):
	"""
	Generates a flask_restful argument parser from the provided required and optional arguments. The
	'acid' (aircraft ID) is always added as the first required parameter.
	:param _req_args: Array of required arguments
	:param opt_args: Array of optional arguments
	:return:
	"""

	req_args = _req_args.copy()
	req_args.insert(0, 'acid')

	parser = reqparse.RequestParser()

	for arg in req_args:
		parser.add_argument(arg, type=str, location='json', required=True)

	if opt_args is not None:
		for arg in opt_args:
			parser.add_argument(arg, type=str, location='json', required=False)

	return parser


def check_acid(string, assert_exists=True):
	"""
	Checks that the given string is a valid ACID, and that it exists in the current simulation.
	Returns a pre-filled Flask response object if the checks fail, or returns None otherwise.
	:param string:
	:param assert_exists: Whether to assert the aircraft already exists or not.
	:return:
	"""

	if not is_acid(string):
		resp = jsonify('Invalid ACID \'{}\''.format(string))
		resp.status_code = 400
		return resp

	if assert_exists and AC_DATA.get(string) is None:
		resp = jsonify('AC {} not found'.format(string))
		resp.status_code = 404
		return resp

	return None


# TODO Allow units to be defined?
# TODO The parser has already been seeded with the required and optional arguments, can we infer
# them here?
def process_ac_cmd(cmd, parser, req_args, opt_args=None, assert_exists=True):
	"""
	Generates a command string using the provided parser and arguments, then sends it to the
	running simulation.
	:param cmd: The name of the command to run
	:param parser:
	:param req_args:
	:param opt_args:
	:param assert_exists: Whether to assert the aircraft already exists or not.
	:return:
	"""

	parsed = parser.parse_args(strict=True)
	acid = parsed['acid']

	resp = check_acid(acid, assert_exists)
	if resp is not None:
		return resp

	cmd_str = '{} {}'.format(cmd, acid)

	for arg in req_args:
		cmd_str += ' {{{}}}'.format(arg)

	cmd_str = cmd_str.format(**parsed)

	if opt_args is not None:
		for opt in opt_args:
			if parsed[opt] is not None:
				cmd_str += ' {}'.format(parsed[opt])

	errprint('Sending stack command: {}'.format(cmd_str))
	bluebird.client.CLIENT_SIM.send_stack_cmd(cmd_str)

	# TODO Get return status. Can check for the created aircraft? What does BlueSky
	# return on an error?
	resp = jsonify('Ok? Command string was: {}'.format(cmd_str))
	resp.status_code = 200
	return resp
