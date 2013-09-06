"""
Robust Twitter crawler primitives.
"""

import json
from time import sleep

import times
from requests_oauthlib import OAuth1

import pypb.req as req

# Constants
RESET_BUFFER      = 5
RATE_LIMIT_BUFFER = 1
RETRY_AFTER       = 60
RETRY_MAX         = 120

from logbook import Logger
log = Logger(__name__)

def rest_rate_limit(r):
    """
    Check the rate limit and sleep it off if hit.
    """

    try:
        #limit  = int(r.headers["X-Rate-Limit-Limit"])
        remain = int(r.headers["X-Rate-Limit-Remaining"])
        reset  = int(r.headers["X-Rate-Limit-Reset"])
        curtime = times.to_unix(times.parse(r.headers["date"]))
    except KeyError as e:
        # We dont have the proper headers
        log.error("Header not found - {}", e)
        sleep(RETRY_AFTER)
        return

    if remain <= RATE_LIMIT_BUFFER:
        log.debug("Hit rate limit - {}", remain)
        log.debug("Rate limit reset in {} seconds", reset - curtime)
        sleep(reset - curtime + RESET_BUFFER)

def statuses_sample(auth):
    """
    Collect the twitter public stream.

    Constantly yields data from the streaming api. Will reconnect the stream
    if it gets disconnected.
    """

    endpoint = "https://stream.twitter.com/1.1/statuses/sample.json"
    auth = OAuth1(signature_type="auth_header", **auth)
    params = {"delimited": 0, "stall_warnings": 1}

    while True:
        r = req.get(endpoint, params=params, auth=auth, timeout=60.0, stream=True)

        if r.status_code == 200:
            for line in r.iter_lines():
                if line:
                    yield json.loads(line)
            continue
    
        # Dont expect anything else
        msg = u"Unexepectd response - {}"
        log.warn(msg, r.status_code)
        sleep(RETRY_AFTER)

def user_timeline(user_id, auth, maxtweets=3200):
    """
    Get as many tweets from the user as possible.

    user_id - A single Twitter user_id.

    Returns an iterable of tweets for the given user.
    """

    endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "user_id": user_id, "count": 200, "include_rts": 1}

    # We gather all tweets here
    tweets = {}
    tcount = 0

    tries = 0
    while tries < RETRY_MAX:
        if tcount >= maxtweets:
            return tweets.itervalues()

        r = req.get(endpoint, params=params, auth=auth, timeout=60.0)

        # Proper receive
        if r.status_code == 200:
            for tweet in r.json():
                tweets[tweet["id"]] = tweet

            # If we have not added any more tweets; return
            if len(tweets) == tcount:
                return tweets.itervalues()
            tcount = len(tweets)

            # Set the new max_id value
            params["max_id"] = min(tweets)
            tries = 0
            rest_rate_limit(r)
            continue

        # Check if rate limited
        if r.status_code == 429:
            log.info(u"Try {}: Being throttled - {} {}",
                     tries, r.status_code, r.text)
            rest_rate_limit(r)
            tries += 1
            continue

        # User doesn't exist
        if r.status_code in (403, 404):
            log.info(u"Try {}: User doesn't exist - {} {}",
                     tries, r.status_code, r.text)
            rest_rate_limit(r)
            return []

        # Dont expect anything else
        log.warn(u"Try {}: Unexepectd response - {} {}",
                 tries, r.status_code, r.text)
        rest_rate_limit(r)
        tries += 1
        continue

    log.critical("Maximum retries exhausted ...")
    raise SystemExit()

def users_lookup(user_ids, auth):
    """
    Lookup profiles of as many users as possible.

    user_ids - A list of Twitter user_ids (max 100).

    Returns a iterable of user profiles. Not all profiles of the users may be
    returned. Twitter lookup api drops user profiles randomly.
    """

    user_ids = map(str, user_ids)
    user_ids = ",".join(user_ids)

    endpoint = "https://api.twitter.com/1.1/users/lookup.json"
    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "user_id": user_ids, "include_entities": 1 }

    tries = 0
    while tries < RETRY_MAX:
        r = req.get(endpoint, params=params, auth=auth, timeout=60.0)

        # Proper receive
        if r.status_code == 200:
            rest_rate_limit(r)
            return r.json()

        # User doesn't exist
        if r.status_code in (403, 404):
            log.info(u"Try {}: User doesn't exist - {} {}",
                     tries, r.status_code, r.text)
            rest_rate_limit(r)
            return []

        # Check if rate limited
        if r.status_code == 429:
            log.info(u"Try {}: Being throttled - {} {}",
                     tries, r.status_code, r.text)
            rest_rate_limit(r)
            tries += 1
            continue

        # Dont expect anything else
        log.warn(u"Try {}: Unexepectd response - {} {}",
                 tries, r.status_code, r.text)
        rest_rate_limit(r)
        tries += 1
        continue

    log.critical("Maximum retries exhausted ...")
    raise SystemExit()

def user_show(user_id, auth):
    """
    Get the profile a single Twitter user.

    user_id - A user_id of a single Twitter user.

    Returns a two tuple. First is the status code returned by Twitter, second is
    the profile of the Twitter user. If status code is 403 or 403, the second
    atrribute will instead contain the reason of absence of the profile.
    """

    endpoint = "https://api.twitter.com/1.1/users/show.json"
    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "user_id": user_id, "include_entities": 1 }

    tries = 0
    while tries < RETRY_MAX:
        r = req.get(endpoint, params=params, auth=auth, timeout=60.0)

        # Proper receive
        if r.status_code == 200:
            rest_rate_limit(r)
            return (200, r.json())

        # User doesn't exist
        if r.status_code in (403, 404):
            rest_rate_limit(r)
            return (r.status_code, r.json())

        # Check if rate limited
        if r.status_code == 429:
            log.info(u"Try {}: Being throttled - {} {}",
                     tries, r.status_code, r.text)
            rest_rate_limit(r)
            tries += 1
            continue

        # Dont expect anything else
        log.warn(u"Try {}: Unexepectd response - {} {}",
                 tries, r.status_code, r.text)
        rest_rate_limit(r)
        tries += 1
        continue

    log.critical("Maximum retries exhausted ...")
    raise SystemExit()

def friend_ids(user_id, auth):
    """
    Get the friend of a single Twitter user.

    user_id - A user_id of a single Twitter user.

    Returns a list of user_ids of users who have been followed by the user.
    """

    endpoint = "https://api.twitter.com/1.1/friends/ids.json"
    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "user_id": user_id, "count": 5000 }

    friends = []

    tries = 0
    nextpage = -1
    while tries < RETRY_MAX:
        params["cursor"] = nextpage
        r = req.get(endpoint, params=params, auth=auth, timeout=60.0)

        # Proper receive
        if r.status_code == 200:
            friends.extend(r.json()["ids"])
            nextpage = r.json()["next_cursor"]
            rest_rate_limit(r)
            if nextpage == 0:
                return friends
        
        # User doesn't exist
        if r.status_code in (403, 404):
            rest_rate_limit(r)
            return []

        # Check if rate limited
        if r.status_code == 429:
            log.info(u"Try {}: Being throttled - {} {}",
                     tries, r.status_code, r.text)
            rest_rate_limit(r)
            tries += 1
            continue

        # Dont expect anything else
        log.warn(u"Try {}: Unexepectd response - {} {}",
                 tries, r.status_code, r.text)
        rest_rate_limit(r)
        tries += 1
        continue

    log.critical("Maximum retries exhausted ...")
    raise SystemExit()

