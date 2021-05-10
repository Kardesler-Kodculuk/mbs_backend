"""
This file contains decorators that can be put on top
    of certain classes to test certain preconditions.
"""
from functools import wraps
from json.decoder import JSONDecodeError
from json import loads, dumps

from flask import Response, request


def requires_json(**decorator_kwargs):
    """
    When decorated with this function, a route is required to have
        at least one argument, this argument will be tested if it
        is valid JSON, furthermore it must also contain the required
        keys if these are provided.

    :param required_keys: In addition to being valid JSON, the payload
        must contain these keys.
    """
    if 'required_keys' not in decorator_kwargs:
        required_keys = []
    else:
        required_keys = decorator_kwargs['required_keys']

    def json_required(route):
        @wraps(route)
        def wrapper(*args, **kwargs):
            """
            The wrapper function.

            :param payload: The wrapped function *must* have at least
                one argument, the first argument of this function will
                be the argument to be tested.
            """
            try:
                data = loads(request.json)
                # Now check if the required keys are all in the data.
                if not all([required_key in data for required_key in required_keys]):
                    resp = Response(dumps({'msg': 'ERROR: Malformed request, does not contain required keys.'}),
                                    status=400, mimetype='application/json')
                else:
                    resp = route(*args, **kwargs)
                return resp
            except JSONDecodeError:
                resp = Response(dumps({'msg': 'ERROR: Expected valid JSON in Request body.'}),
                                status=400, mimetype='application/json')
                return resp
        return wrapper
    return json_required


def returns_json(route):
    """
    Routes decorated with this decorator will get their first return argument
        converted to JSON and their second interpreted as the return status code,
        the content type will be set to application/json.
    """
    @wraps(route)
    def wrapper(*args, **kwargs):
        try:
            value, status = route(*args, **kwargs)
            return Response(dumps(value), status=status, mimetype='application/json')
        except ValueError:
            raise TypeError("Expected the function return type to be tuple[dict, int].")
    return wrapper


def full_json(**decorator_kwargs):
    """
    Routes decorated with this decorator expect JSON in their request
        body and return json as a response.
    """
    def decorator(route):
        @wraps(route)
        def wrapper(*args, **kwargs):
            return returns_json(requires_json(**decorator_kwargs)(route))(*args, **kwargs)  # Apply the two decorators.
        return wrapper
    return decorator
