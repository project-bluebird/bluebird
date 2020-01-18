"""
Contains utility methods to create Flask responses
"""
from http import HTTPStatus
from typing import Dict
from typing import Optional
from typing import Union

from flask import jsonify
from flask import make_response

from bluebird.settings import Settings


def internal_err_resp(err: str):
    """
    Generates a standard flask error response for a given error
    """
    return make_response(err, HTTPStatus.INTERNAL_SERVER_ERROR)


def not_found_resp(err: str):
    """
    Generates a standard NOT_FOUND flask response
    """
    return make_response(err, HTTPStatus.NOT_FOUND)


def _make_response_from_data(data: Optional[Union[str, Dict]], status: HTTPStatus):
    if isinstance(data, dict):
        data = jsonify(data)
    elif not data:
        data = ""
    return make_response(data, status)


def ok_resp(data: Optional[Union[str, Dict]] = None):
    """Generates a standard OK response"""
    return _make_response_from_data(data, HTTPStatus.OK)


def created_resp(data: Optional[Union[str, Dict]] = None):
    """Generates a standard CREATED response"""
    return _make_response_from_data(data, HTTPStatus.CREATED)


def bad_request_resp(msg: str):
    """
    Generates a standard BAD_REQUEST response with the given message
    """
    return make_response(msg, HTTPStatus.BAD_REQUEST)


def checked_resp(err: Optional[str], code: HTTPStatus = HTTPStatus.OK):
    """
    Generates a standard response or an INTERNAL_SERVER_ERROR response depending on the
    value of err
    """
    if err:
        return internal_err_resp(err)
    return make_response("", code)


# TODO(RKM 2019-11-26) Make sure this is used throughout the API when needed
def not_implemented_resp(api: str):
    """
    Generates a standard NOT_IMPLEMENTED response
    """
    return make_response(
        f"API '{api}' not currently supported for sim type '{Settings.SIM_TYPE.name}'",
        HTTPStatus.NOT_IMPLEMENTED,
    )
