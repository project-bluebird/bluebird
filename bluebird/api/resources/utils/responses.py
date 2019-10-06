"""
Contains utility methods to create Flask responses
"""


from http import HTTPStatus
from typing import Optional, Tuple

from flask import jsonify

from bluebird.settings import Settings


RespTuple = Tuple[str, HTTPStatus]


def internal_err_resp(err: str) -> RespTuple:
    """
    Generates a standard flask error response for a given error
    """
    return (err, HTTPStatus.INTERNAL_SERVER_ERROR)


def not_found_resp(err: str) -> RespTuple:
    """
    Generates a standard NOT_FOUND flask response
    """
    return (err, HTTPStatus.NOT_FOUND)


def ok_resp(data: dict = None) -> RespTuple:
    """
    Generates a standard response
    """
    if data:
        return (jsonify(data), HTTPStatus.OK)
    return ("", HTTPStatus.OK)


def not_implemented_resp() -> RespTuple:
    """
    Generates a standard response for APIs which are not implemented for the current
    simulator
    """
    return (
        f"API is not supported for the {Settings.SIM_TYPE.name} simulator",
        HTTPStatus.NOT_IMPLEMENTED,
    )


def bad_request_resp(msg: str) -> RespTuple:
    """
    Generates a standard BAD_REQUEST response with the given message
    """
    return (msg, HTTPStatus.BAD_REQUEST)


def checked_resp(err: Optional[str], code: HTTPStatus = HTTPStatus.OK) -> RespTuple:
    """
    Generates a standard response or an INTERNAL_SERVER_ERROR response depending on the
    value of err
    """
    if err:
        return internal_err_resp(err)
    return ("", code)
