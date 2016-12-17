"""
Foursquare API
"""

import time
import pprint

import logbook

from wriggler import Error
import wriggler.const as const
import wriggler.req as req
from wriggler.check_rate_limit import check_rate_limit

log = logbook.Logger(__name__)

VERSION = 20150425
MODE = "foursquare"

# Error code and error type code meaning taken from:
# https://developer.foursquare.com/overview/responses
# Accessd on: April 25, 2015
ERROR_CODES = {
    400: ("Bad Request",
          "Any case where a parameter is invalid, "
          "or a required parameter is missing. "
          "This includes the case where no OAuth token is provided "
          "and the case where a resource ID is "
          "specified incorrectly in a path."),
    401: ("Unauthorized",
          "The OAuth token was provided but was invalid."),
    403: ("Forbidden",
          "The requested information cannot be viewed by the acting user, "
          "for example, because they are not friends with the user "
          "whose data they are trying to read."),
    404: ("Not Found",
          "Endpoint does not exist."),
    405: ("Method Not Allowed",
          "Attempting to use POST with a GET-only endpoint, or vice-versa."),
    409: ("Conflict",
          "The request could not be completed as it is. "
          "Use the information included in the response "
          "to modify the request and retry."),
    500: ("Internal Server Error",
          "Foursquare's servers are unhappy. "
          "The request is probably valid but needs to be retried later.")
}

ERROR_TYPE_CODES = {
    "invalid_auth":
        ("OAuth token was not provided or was invalid."),
    "param_error":
        ("A required parameter was missing or a parameter was malformed. "
         "This is also used if the resource ID in the path is incorrect."),
    "endpoint_error":
        ("The requested path does not exist."),
    "not_authorized":
        ("Although authentication succeeded, "
         "the acting user is not allowed to see this information "
         "due to privacy restrictions."),
    "rate_limit_exceeded":
        ("Rate limit for this hour exceeded."),
    "deprecated":
        ("Something about this request is using deprecated functionality, "
         "or the response format may be about to change."),
    "server_error":
        ("Server is currently experiencing issues. "
         "Check status.foursquare.com for updates."),
    "other":
        ("Some other type of error occurred.")
}

class FoursquareError(Error):
    """
    Error returned from Foursquare api.
    """

    def __init__(self, response, tries):
        super(FoursquareError, self).__init__(response, tries)

        self.response = response
        self.tries = tries

        self.http_status_code = response.status_code
        try:
            self.body = response.json()
            self.parsed_body = True
        except ValueError:
            self.body = response.text
            self.parsed_body = False

        if self.parsed_body:
            try:
                self.error_type = self.body["meta"]["errorType"]
            except KeyError:
                self.error_type = None

            try:
                self.error_detail = self.body["meta"]["errorDetail"]
            except KeyError:
                self.error_detail = None
        else:
            self.error_type = None
            self.error_detail = None

    def __repr__(self):
        fmt = "FoursquareError(http_status_code={0},error_type={1})"
        return fmt.format(self.http_status_code, self.error_type)

    def __str__(self):
        htext, hdesc = ERROR_CODES.get(self.http_status_code,
                                       ("Unknown", "Unknown"))

        edesc = ERROR_TYPE_CODES.get(self.error_type, "Unknown")

        if self.parsed_body:
            btext = pprint.pformat(self.body, indent=2)
        else:
            btext = self.body

        fmt = ("FoursquareError\n"
               "http_status_code: {0} - {1}\n{2}\n"
               "error_type: {3}\n{4}\n"
               "error_detail:\n{5}\n"
               "--------\n{6}")
        return fmt.format(self.http_status_code, htext, hdesc,
                          self.error_type, edesc,
                          self.error_detail,
                          btext)

def rest_api_call(endpoint, auth, accept_codes, params):
    """
    Call the rest api endpoint.
    """

    # Add version info into the code
    params.setdefault("client_id", auth["client_id"])
    params.setdefault("client_secret", auth["client_secret"])
    params.setdefault("v", VERSION)
    params.setdefault("m", MODE)

    tries = 0
    while tries < const.API_RETRY_MAX:
        r = req.get(endpoint, params=params, timeout=60.0)

        # Proper receive
        if 200 <= r.status_code < 300 or r.status_code in accept_codes:
            time.sleep(check_rate_limit(r.headers))

            try:
                data = r.json()
            except ValueError:
                log.info(u"Try L1 {}: Falied to decode Json - {}\n{}",
                         tries, r.status_code, r.text)
                tries += 1
                continue

            return (data, r.status_code)

        # Check if rate limited
        if r.status_code in 403:
            log.info(u"Try L1 {}: Being throttled - {}\n{}",
                     tries, r.status_code, r.text)
            time.sleep(check_rate_limit(r.headers))
            tries += 1
            continue

        # Server side error; Retry after delay
        if 500 <= r.status_code < 600:
            log.info(u"Try L1 {}: Server side error {}\n{}",
                     tries, r.status_code, r.text)
            time.sleep(check_rate_limit(r.headers))
            tries += 1
            continue

        # Some other error; Break out of loop
        break

    # Give up
    raise FoursquareError(r, tries)

def venues_explore(auth, **params):
    """
    Call the venues, explore api.
    """

    endpoint = "https://api.foursquare.com/v2/venues/explore"
    accept_codes = ()

    return rest_api_call(endpoint, auth, accept_codes, params)

