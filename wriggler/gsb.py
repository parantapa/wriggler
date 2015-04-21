"""
Python API for Google Safe Browsing Lookup API
"""

import time

from wriggler import log, Error
import wriggler.const as const
import wriggler.req as req

CLIENT = "wriggler.gsb"
PVER = 3.0
ENDPOINT = "https://sb-ssl.google.com/safebrowsing/api/lookup"

# max request body size
MAX_SIZE = 10 * 1024

ERROR_CODES = {
    400: ("Bad Request", "The HTTP request was not correctly formed"),
    401: ("Not Authorized", "The apikey is not authorized"),
    503: ("Service Unavailable",
          "The server cannot handle the request.\nBesides the normal server"
          "failures, it could also indicate that the client"
          "has been \"throttled\" by sending too many requests")
}

class GoogleSafeBrowsingError(Error):
    """
    Error returned from google safe browsing api.
    """

    def __init__(self, response, tries):
        super(GoogleSafeBrowsingError, self).__init__(response, tries)

        self.response = response
        self.tries = tries

        self.http_status_code = response.status_code
        self.body = response.text

    def __repr__(self):
        fmt = "GoogleSafeBrowsingError(http_status_code={0})"
        return fmt.format(self.http_status_code)

    def __str__(self):
        etext, edesc = ERROR_CODES.get(self.http_status_code,
                                       ("Unknown", "Unknown"))
        body = unicode(self.body).encode("utf-8")

        hdr = "GoogleSafeBrowsingError\nhttp_status_code: {0} - {1}\n{2}"
        hdr = hdr.format(self.http_status_code, etext, edesc)
        return hdr + "\n--------\n" + body

def make_body(urls):
    """
    Create the body of the next request.
    """

    us, body = [], ""

    for url in urls:
        us.append(url)
        body = body + "\n" + url

        if len(us) == 500 or len(body) >= MAX_SIZE:
            yield us, str(len(us)) + body
            us, body = [], ""

    if us:
        yield us, str(len(us)) + body

def do_lookup(auth, urls, data):
    """
    Do the actual call.
    """

    # Generate the get params
    params = {"client": CLIENT, "appver": 0.1, "apikey": auth, "pver": PVER}

    # Make the request
    tries = 0
    while tries < const.API_RETRY_MAX:
        r = req.post(ENDPOINT, params=params, data=data, timeout=60.0)

        # We have at least one match
        if r.status_code == 200:
            ret = r.text
            ret = ret.split("\n")
            ret = dict(zip(urls, ret))
            return ret, r.status_code

        # All the urls are good
        if r.status_code == 204:
            return {u: "ok" for u in urls}, r.status_code

        # Server side error Retry
        if 500 <= r.status_code < 600:
            log.info(u"Try L1 {}: Server side error {} {}",
                tries, r.status_code, r.text)
            time.sleep(const.API_RETRY_AFTER)

        # Some other error
        break

    raise GoogleSafeBrowsingError(r, tries)

def lookup(auth, urls):
    """
    Check ecah url using Google Safe Browsing Lookup API.

    Returns a dict mapping each url to the api response.

    key  - API Key
    urls - List of urls to check
    """

    for us, data in make_body(urls):
        resp = do_lookup(auth, us, data)
        yield resp
