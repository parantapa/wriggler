"""
A simple and robust way for making http requests.

This library wraps python-requests. The errors handled by this module are
connection requests and server side errors. The error handling strategy
is quite simple. Wait for fixed number of seconds on error and then retry.
"""

import requests
from time import sleep

from wriggler import log, Error
import wriggler.const as const

class ConnectFailError(Error):
    """
    Raised on error cases.
    """

def robust_http(args, kwargs, method):
    """
    Repeat the HTTP GET/POST operatopn in case of failure.
    """

    # Keep trying for downlod
    for tries in xrange(const.CONNECT_RETRY_MAX):
        try:
            return method(*args, **kwargs)
        except requests.RequestException as e:
            msg = u"Try L0: {} - Get Failed: {}: {}"
            log.info(msg, tries, type(e), e)
            sleep(const.CONNECT_RETRY_AFTER)
        except Exception as e:
            msg = u"Try L0: {} - Get Failed: {}: {}"
            log.warn(msg, tries, type(e), e)
            sleep(const.CONNECT_RETRY_AFTER)

    # Cant help any more; Quit program
    msg = "Falied to make http request!"
    log.critical(msg)
    raise ConnectFailError(msg)

def get(*args, **kwargs):
    """
    Perform a robust GET request.
    """

    session = kwargs.get("session", None)
    if session is None:
        return robust_http(args, kwargs, requests.get)
    else:
        return robust_http(args, kwargs, session.get)

def post(*args, **kwargs):
    """
    Perform a robust POST request.
    """

    session = kwargs.get("session", None)
    if session is None:
        return robust_http(args, kwargs, requests.post)
    else:
        return robust_http(args, kwargs, session.post)

