"""
Contains utility methods to create Flask responses
"""


from http import HTTPStatus
from typing import Optional

from flask import jsonify, make_response

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


def ok_resp(data: dict = None):
    """
    Generates a standard response
    """
    body = jsonify(data) if data else ""
    return make_response(body, HTTPStatus.OK)


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


def not_implemented_resp(api: str):
    """
    Generates a standard NOT_IMPLEMENTED response
    """
    return make_response(
        f"API '{api}' not currently supported for sim type '{Settings.SIM_TYPE.name}'",
        HTTPStatus.NOT_IMPLEMENTED,
    )
