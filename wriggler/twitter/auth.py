"""
Defines the multi auth object for multiple key management.
"""

import sys
import time
import json

import times

from wriggler import log
import wriggler.const as const

class MultiAuth(object):
    """
    Manage multiple twitter keys.
    """

    def __init__(self, keys):
        super(MultiAuth, self).__init__()

        now = times.to_unix(times.now())

        self.idx    = 0
        self.keys   = keys
        self.remain = [sys.maxsize] * len(keys)
        self.reset  = [now + const.TWITTER_DEFAULT_WINDOW_TIME] * len(keys)

    def get_token(self):
        """
        Get a token for the call.
        """

        return self.keys[self.idx]

    def check_limit(self, headers):
        """
        Check if rate limit is hit for the current key.
        """

        now = times.to_unix(times.now())

        try:
            curtime = times.to_unix(times.to_universal(headers["date"]))
            self.remain[self.idx] = int(headers["X-Rate-Limit-Remaining"])
            self.reset[self.idx]  = int(headers["X-Rate-Limit-Reset"]) - curtime
        except KeyError as e:
            log.warn(u"Header not found! - {} {}", type(e), e)
            time.sleep(const.API_RETRY_MAX)
            return

        # Reset time in our system time
        self.reset[self.idx] += now + const.TWITTER_RATE_LIMIT_RESET_BUFFER

        # If we hit rate limit switch to the next key
        if self.remain[self.idx] <= const.TWITTER_RATE_LIMIT_BUFFER:
            log.debug("Key {} hit rate limit ...", self.idx)
            self.idx = (self.idx + 1) % len(self.keys)

            # The next key had also hit rate limit previously
            # Sleep off the rate limit window
            if (self.remain[self.idx] <= const.TWITTER_RATE_LIMIT_BUFFER
                    and self.reset[self.idx] > now):
                log.debug("Key {} still in rate limit ...", self.idx)
                time.sleep(self.reset[self.idx] - now)

def chunks(l, n):
    """
    Yield successive n-sized chunks from l.
    """

    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def read_multi_auth(fname):
    """
    Read multiple keys from file.
    """

    log.debug("Reading keys from {} ...", fname)
    with open(fname) as fobj:
        keys = json.load(fobj)

    return MultiAuth(keys)

def read_multi_auths(fname, size=sys.maxsize):
    """
    Read multiple keys from file split into size blocks.
    """

    log.debug("Reading keys from {} ...", fname)
    with open(fname) as fobj:
        keys = json.load(fobj)

    ks = list(chunks(keys, size))
    auths = [MultiAuth(k) for k in ks]

    return auths

