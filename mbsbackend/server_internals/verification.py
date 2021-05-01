"""
This file contains decorators that can be put on top
    of certain classes to test certain preconditions.
"""
from json.decoder import JSONDecodeError
from typing import Tuple, Callable
from json import loads


def _is_json(string_: str) -> bool:
    """
    Test if a given string is in fact stringified
        JSON.

    :param string_: String to test.
    :return True if the string_ is a valid JSON.
    https://stackoverflow.com/a/11294685/6663851
    """
    try:
        loads(string_)
    except JSONDecodeError:  # If an error occurs during parsing
        return False  # It is not JSON.
    return True  # Otherwise, it is.


def json_required(route):
    """
    When decorator with JSON required, the decorated route
        is tested to make sure its payload takes a JSON form,
        if it is not valid JSON 400 status code will be returned.
    """
    def wrapper(payload, *args, **kwargs):
        """
        The wrapper function.

        :param payload: The wrapped function *must* have at least
            one argument, the first argument of this function will
            be the argument to be tested.
        """
        if not _is_json(payload):
            return "ERROR: Expected valid JSON in Request body.", 400
        return route(*args, **kwargs)
    return wrapper

