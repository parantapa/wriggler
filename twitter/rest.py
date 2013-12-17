"""
Robust Twitter crawler primitives.
"""

from requests_oauthlib import OAuth1

import pypb.req as req

from logbook import Logger
log = Logger(__name__)

GIVE_UP_AFTER = 24 * 3600
RETRY_AFTER   = 5
RETRY_MAX     = GIVE_UP_AFTER // RETRY_AFTER

def list_to_csv(args):
    """
    Convert a list to a string csv.
    """

    args = map(str, args)
    args = ",".join(args)
    return args

class Error(Exception):
    """
    Unrecoverable Error.
    """

class RetryExhausted(Error):
    """
    Maximum retry count exhausted.
    """

def twitter_rest_call(endpoint, auth, accept_codes, params):
    """
    Call a Twitter rest api endpoint.
    """

    oauth = OAuth1(signature_type="auth_header", **auth.get_token())

    tries = 0
    while tries < RETRY_MAX:
        r = req.get(endpoint, params=params, auth=oauth, timeout=60.0)

        # Proper receive
        if 200 <= r.status_code < 300 or r.status_code in accept_codes:
            auth.check_limit(r.headers)
            return (r.json(), r.status_code)

        # Check if rate limited
        if r.status_code == 429:
            log.info(u"Try {}: Being throttled - {} {}",
                     tries, r.status_code, r.text)
            auth.check_limit(r.headers)
            tries += 1
            continue

        # Client side error; Can't handle here
        if 400 <= r.status_code < 500:
            log.error(u"Try {}: Client side error - {} {}",
                      tries, r.status_code, r.text)
            raise Error("Client side error", r.status_code, r.text)

        # Server side error; Retry after delay
        if 500 <= r.status_code < 600:
            log.info(u"Try {}: Server side error {} {}",
                     tries, r.status_code, r.text)
            auth.check_limit(r.headers)
            tries += 1

        # Dont expect anything else
        log.warn(u"Try {}: Unexepectd response - {} {}",
                 tries, r.status_code, r.text)
        auth.check_limit(r.headers)
        tries += 1
        continue

    log.critical("Maximum retries exhausted ...")
    raise RetryExhausted(endpoint, params)

def users_show(auth, **params):
    """
    Return the information for a single user.
    """

    endpoint = "https://api.twitter.com/1.1/users/show.json"
    accept_codes = (401, 403, 404)

    params.setdefault("include_entities", 1)

    return twitter_rest_call(endpoint, auth, accept_codes, params)

def users_lookup(auth, **params):
    """
    Lookup profiles of as many users as possible.
    """

    endpoint = "https://api.twitter.com/1.1/users/lookup.json"
    accept_codes = (403, 404)

    params.setdefault("include_entities", 1)
    if "user_id" in params:
        params["user_id"] = list_to_csv(params["user_id"])
    if "screen_name" in params:
        params["screen_name"] = list_to_csv(params["screen_name"])

    return twitter_rest_call(endpoint, auth, accept_codes, params)

def statuses_user_timeline(auth, **params):
    """
    Get the user timeline of a single user.
    """

    endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    accept_codes = (403, 404)

    params.setdefault("include_rts", 1)
    params.setdefault("count", 200)

    return twitter_rest_call(endpoint, auth, accept_codes, params)

def friends_ids(auth, **params):
    """
    Get the friend ids of a given user.
    """

    endpoint = "https://api.twitter.com/1.1/friends/ids.json"
    accept_codes = (403, 404)

    params.setdefault("count", 5000)

    return twitter_rest_call(endpoint, auth, accept_codes, params)

def followers_ids(auth, **params):
    """
    Get the friend ids of a given user.
    """

    endpoint = "https://api.twitter.com/1.1/followers/ids.json"
    accept_codes = (403, 404)

    params.setdefault("count", 5000)

    return twitter_rest_call(endpoint, auth, accept_codes, params)

def search_tweets(auth, **params):
    """
    Search twitter for tweets.
    """

    endpoint = 'https://api.twitter.com/1.1/search/tweets.json'
    accept_codes = ()

    params.setdefault("count", 100)
    params.setdefault("include_entities", "true")

    return twitter_rest_call(endpoint, auth, accept_codes, params)

