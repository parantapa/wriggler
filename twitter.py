"""
Robust Twitter crawler primitives.
"""

import sys
import json
from time import sleep

import times
from requests_oauthlib import OAuth1

import pypb.req as req

# Constants
RESET_BUFFER      = 5
RATE_LIMIT_BUFFER = 1
RETRY_AFTER       = 5
RETRY_MAX         = 120

from logbook import Logger
log = Logger(__name__)

class Error(Exception):
    """
    Unrecoverable Error.
    """

class RetryExhausted(Error):
    """
    Maximum retry count exhausted.
    """

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

def user_timeline(user_id=None, screen_name=None, auth=None, maxtweets=sys.maxsize):
    """
    Get as many tweets from the user as possible.

    user_id - A single Twitter user_id.
    screen_name - A single Twitter screen name.

    NOTE: Only one of user_id or screen_name must be passed.

    Returns an iterable of tweets for the given user.
    """

    assert bool(user_id is not None) != bool(screen_name is not None)
    assert auth is not None

    endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "count": 200, "include_rts": 1}
    if user_id is not None:
        params["user_id"] = user_id
    if screen_name is not None:
        params["screen_name"] = screen_name

    # We gather all tweet ids here
    tweets = set()
    tcount = 0

    tries = 0
    while tries < RETRY_MAX:
        if tcount >= maxtweets:
            return

        r = req.get(endpoint, params=params, auth=auth, timeout=60.0)

        # Proper receive
        if r.status_code == 200:
            for tweet in r.json():
                if tweet["id"] not in tweets:
                    tweets.add(tweet["id"])
                    yield tweet

            # If we have not added any more tweets; return
            if len(tweets) == tcount:
                return
            tcount = len(tweets)

            # Set the new max_id value
            params["max_id"] = min(tweets) - 1
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
            return

        # Dont expect anything else
        log.warn(u"Try {}: Unexepectd response - {} {}",
                 tries, r.status_code, r.text)
        rest_rate_limit(r)
        tries += 1
        continue

    log.critical("Maximum retries exhausted ...")
    raise RetryExhausted(user_id, auth, maxtweets)

def users_lookup(user_ids=None, screen_names=None, auth=None):
    """
    Lookup profiles of as many users as possible.

    user_ids - A list of Twitter user_ids (max 100).
    screen_names - A list of Twitter screen names (max 100).
    
    NOTE: Only one of user_ids or screen_names should be passed.

    Returns a iterable of user profiles. Not all profiles of the users may be
    returned. Twitter lookup api drops user profiles randomly.
    """

    assert bool(user_ids is not None) != bool(screen_names is not None)
    assert auth is not None

    endpoint = "https://api.twitter.com/1.1/users/lookup.json"
    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "include_entities": 1 }
    if user_ids is not None:
        user_ids = map(str, user_ids)
        user_ids = ",".join(user_ids)
        params["user_id"] = user_ids
    if screen_names is not None:
        screen_names = ",".join(screen_names)
        params["screen_name"] = screen_names

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
    raise RetryExhausted(user_ids, auth)

def user_show(user_id=None, screen_name=None, auth=None):
    """
    Get the profile a single Twitter user.

    user_id - user_id of a single Twitter user.
    screen_name - screen name of a single twitter user.
    
    NOTE: Only one of user_id or screen_name should be passed.

    Returns a two tuple. First is the status code returned by Twitter, second is
    the profile of the Twitter user. If status code is 403 or 403, the second
    atrribute will instead contain the reason of absence of the profile.
    """

    assert bool(user_id is not None) != bool(screen_name is not None)
    assert auth is not None

    endpoint = "https://api.twitter.com/1.1/users/show.json"
    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "include_entities": 1 }
    if user_id is not None:
        params["user_id"] = user_id
    if screen_name is not None:
        params["screen_name"] = screen_name

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
    raise RetryExhausted(user_id, auth)

def _friend_or_follower_ids(endpoint, user_id, auth, maxids):
    """
    Backend of friend_ids and follower_ids.
    """

    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "user_id": user_id, "count": 5000 }

    ids = []

    tries = 0
    nextpage = -1
    while tries < RETRY_MAX:
        params["cursor"] = nextpage
        r = req.get(endpoint, params=params, auth=auth, timeout=60.0)

        # Proper receive
        if r.status_code == 200:
            ids.extend(r.json()["ids"])
            if len(ids) >= maxids:
                return ids[:maxids]

            nextpage = r.json()["next_cursor"]
            rest_rate_limit(r)
            if nextpage == 0:
                return ids
        
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
    raise RetryExhausted(user_id, auth)

def friends_ids(user_id, auth, maxids=sys.maxsize):
    """
    Get the friends of a single Twitter user.

    user_id - A user_id of a single Twitter user.

    Returns a list of user_ids of users who have been followed by the user.
    """

    endpoint = "https://api.twitter.com/1.1/friends/ids.json"
    return _friend_or_follower_ids(endpoint, user_id, auth, maxids)

def followers_ids(user_id, auth, maxids=sys.maxsize):
    """
    Get the followers of a single Twitter user.

    user_id - A user_id of a single Twitter user.

    Returns a list of user_ids of users who have followed the user.
    """

    endpoint = "https://api.twitter.com/1.1/followers/ids.json"
    return _friend_or_follower_ids(endpoint, user_id, auth, maxids)

def search_tweets(query, result_type, auth, maxtweets=sys.maxsize):
    """
    Get as many tweets from twitter search as possible.

    query - The twitter search query
    result_type - mixed, recent, popular

    Returns an iterable of tweets.
    """

    endpoint = 'https://api.twitter.com/1.1/search/tweets.json'
    auth = OAuth1(signature_type="auth_header", **auth)
    params = { "q": query, "result_type": result_type, "count": 100,
               "include_entities": "true" }

    # We gather all tweet ids here
    maxid = float("inf")
    tcount = 0

    tries = 0
    while tries < RETRY_MAX:
        r = req.get(endpoint, params=params, auth=auth, timeout=60.0)

        # Proper receive
        if r.status_code == 200:
            data = r.json()
            for tweet in data["statuses"]:
                yield tweet
                maxid = min(tweet["id"], maxid)
                tcount += 1
                if tcount >= maxtweets:
                    return

            # Set the new max_id value
            params["max_id"] = maxid - 1
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

        # Dont expect anything else
        log.warn(u"Try {}: Unexepectd response - {} {}",
                 tries, r.status_code, r.text)
        rest_rate_limit(r)
        tries += 1
        continue

    log.critical("Maximum retries exhausted ...")
    raise RetryExhausted(query, result_type, auth, maxtweets=sys.maxsize)

