"""
Tests functionality of the bluebird.api.resources.utils module
"""

from flask import Flask
from flask_restful.reqparse import RequestParser

import bluebird.client
from bluebird.api.resources.utils import check_acid, generate_arg_parser, process_ac_cmd
from . import TEST_ACIDS


def test_generate_arg_parser():
	"""
	Tests that our generation of the argument parser is correct
	:return:
	"""

	req_args = ['req1', 'req2']
	opt_args = ['opt1']

	parser = generate_arg_parser(req_args, opt_args)
	args = parser.args

	assert isinstance(parser, RequestParser), 'Expected a RequestParser object'
	assert len(args) == 1 + len(req_args) + len(opt_args), 'Expected the correct number of args'
	assert all(x.location == 'json' for x in args), 'Expected all args to be in the request JSON'

	assert args[0].name == 'acid', 'Expected that the first arg is \'acid\''
	assert args[0].required, 'Expected \'acid\' to be a required argument'

	idx = 1

	for req in req_args:
		assert args[idx].name == req, 'Expected the arg name to be \'{}\''.format(req)
		assert args[idx].required, 'Expected \'{}\' to be a required argument'.format(req)
		idx += 1

	for opt in opt_args:
		assert args[idx].name == opt, 'Expected the arg name to be \'{}\''.format(opt)
		assert not args[idx].required, 'Expected \'{}\' to be an optional argument'.format(opt)
		idx += 1


def test_check_acid():
	"""
	Tests that check_acid performs correctly
	:return:
	"""

	app = Flask(__name__)

	with app.test_request_context():
		# Check invalid ACID is rejected
		test_acid = 'T'
		resp = check_acid(test_acid)
		assert resp.status == '400 BAD REQUEST', 'Expected invalid acid to return bad request'
		assert resp.get_json() == 'Invalid ACID \'{}\''.format(
						test_acid), 'Expected appropriate message'

		# Check valid ACID is accepted
		test_acid = 'TST1003'
		assert test_acid not in TEST_ACIDS, 'test_acid should not exist in the package' \
		                                    'TEST_ACIDS array!'

		resp = check_acid(test_acid, assert_exists=False)
		assert resp is None, 'Expected resp to be None from a valid acid (assert_exists=False)'

		# Check that assert_exists behaves correctly for a missing aircraft
		resp = check_acid(test_acid, assert_exists=True)
		assert resp.status == '404 NOT FOUND', 'Expected 404 not found response for missing aircraft'
		assert resp.get_json() == 'AC {} not found'.format(test_acid), 'Expected appropriate message'

		# Checks that a valid acid of an existing aircraft is accepted
		test_acid = TEST_ACIDS[0]
		resp = check_acid(test_acid, assert_exists=True)
		assert resp is None, 'Expected None from an existing aircraft with (assert_exists=True)'


def test_process_ac_cmd(patch_client_sim):
	# pylint: disable=unused-argument

	"""
	Tests that process_ac_cmd performs correctly
	:param patch_client_sim:
	:return:
	"""

	cmd = 'TST'
	acid = 'TST1001'
	req_args = ['req1', 'req2']
	opt_args = ['opt1', 'opt2']

	parser = generate_arg_parser(req_args, opt_args)
	json = {'acid': acid, 'req1': 1, 'req2': 2, 'opt1': 3, 'opt2': 4}

	app = Flask(__name__)

	with app.test_request_context('/', json=json):
		resp = process_ac_cmd(cmd, parser, req_args, opt_args, assert_exists=False)

	assert resp is not None, ''
	assert resp.status == '200 OK'

	expected = '{} {} {} {} {} {}'.format(cmd, acid, 1, 2, 3, 4)
	assert bluebird.client.CLIENT_SIM.last_stack_cmd == expected, ''  # pylint: disable=no-member

	json = {'acid': acid, 'req1': 1, 'req2': 2, 'opt2': 5}

	with app.test_request_context('/', json=json):
		resp = process_ac_cmd(cmd, parser, req_args, opt_args, assert_exists=False)

	assert resp is not None, ''
	assert resp.status == '200 OK'

	expected = '{} {} {} {} {}'.format(cmd, acid, 1, 2, 5)
	assert bluebird.client.CLIENT_SIM.last_stack_cmd == expected, ''  # pylint: disable=no-member
