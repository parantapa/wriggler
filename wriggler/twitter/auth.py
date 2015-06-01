"""
Defines the multi auth object for multiple key management.
"""

import sys
import time
import json

import arrow
from dateutil.parser import parse

from wriggler import log
import wriggler.const as const

from wriggler.check_rate_limit import check_rate_limit

class MultiAuth(object):
    """
    Manage multiple twitter keys.
    """

    def __init__(self, keys):
        super(MultiAuth, self).__init__()

        now = arrow.now().timestamp

        self.idx = 0
        self.keys = keys
        self.reset = [now] * len(keys)

    def get_token(self):
        """
        Get a token for the call.
        """

        return self.keys[self.idx]

    def check_limit(self, headers):
        """
        Check if rate limit is hit for the current key.
        """

        now = arrow.now().timestamp
        sleep_time = check_rate_limit(headers)

        if sleep_time:
            log.debug("Key {} hit rate limit ...", self.idx)

            # Save the reset time
            self.reset[self.idx] = now + sleep_time

            # Move on to the next key
            self.idx = (self.idx + 1) % len(self.keys)

            # If the next key is also under ratelimit,
            # sleep off the rate limit window
            if self.reset[self.idx] > now:
                log.debug("Key {} still in rate limit ...", self.idx)
                time.sleep(self.reset[self.idx] - now)

def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """

    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def read_keys(fname):
    """
    Read multiple keys from file.
    """

    log.debug("Reading keys from {} ...", fname)
    with open(fname) as fobj:
        keys = json.load(fobj)

    return MultiAuth(keys)

def read_keys_split(fname, size=sys.maxsize):
    """
    Read multiple keys from file split into size blocks.
    """

    log.debug("Reading keys from {} ...", fname)
    with open(fname) as fobj:
        keys = json.load(fobj)

    ks = list(chunks(keys, size))
    auths = [MultiAuth(k) for k in ks]

    return auths

