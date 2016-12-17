"""
API for BingSearch Web
"""

import time
from base64 import b64encode

import logbook

import wriggler.const as const
import wriggler.req as req

from wriggler.azure import AzureError

log = logbook.Logger(__name__)

ENDPOINT = "https://api.datamarket.azure.com/Bing/SearchWeb/v1/Web"

def search(auth, query, **params):
    """
    Return the results web search query from Bing.
    """

    auth = "Basic " + b64encode(":" + auth)
    auth_header = {"Authorization": auth}

    params.setdefault("$format", "json")
    params.setdefault("Query", "'%s'" % query)

    tries = 0
    while tries < const.API_RETRY_MAX:
        r = req.get(ENDPOINT, params=params, headers=auth_header, timeout=60.0)

        # Proper receive
        if 200 <= r.status_code < 300:

            try:
                data = r.json()
            except ValueError:
                log.info(u"Try L1 {}: Falied to decode JSON - {}\n{}",
                         tries, r.status_code, r.text)
                tries += 1
                continue

            return (data, r.status_code)

        # Server side error; Retry after delay
        if 500 <= r.status_code < 600:
            log.info(u"Try L1 {}: Server side error {}\n{}",
                     tries, r.status_code, r.text)
            time.sleep(const.API_RETRY_AFTER)

            tries += 1
            continue

        # Some other error; Break out of loop
        break

    # Give up
    raise AzureError(r, tries)
