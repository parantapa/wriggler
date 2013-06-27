"""
Robust Twitter crawler primitives.
"""

from time import sleep

import req
import times
from requests_oauthlib import OAuth1

# Constants
RESET_BUFFER      = 5
RATE_LIMIT_BUFFER = 1
RETRY_AFTER       = 60
RETRY_MAX         = 120

from logbook import Logger
log = Logger(__name__)

#def stream_rate_limit(r, count):
    #"""
    #Check the rate limit and sleep off if it is hit.

    #r - The response object from requests.
    #"""
    ## In case of rate limit back off exponentially,
    ## start with a 1 minute wait and double each attempt.
    #if (r.status_code == 420):
        #sleeptime = WAIT_TIME ** count[0]
        #count[0] = count[0] * 2
        #sleep(sleeptime)
    ## In case of other http error back off exponentially
    ## starting with 5 seconds doubling each attempt, up to 320 seconds.
    #else:
        #sleeptime = min(FAILURE_WAIT ** count[0], 320)
        #count[0] = count[0] * 2
        #sleep(sleeptime)

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

#def public_stream (token):
    #"""
    #To collect tweets using public stream.

    #param - A list of the field based on which tweets needs to be collected
    #token - A list containing client_key, client_secret , resource_owner_key, resource_owner_secret
    #"""
    #count = []
    #httpcount = []
    #count.append(1)
    #httpcount.append(1)
    #url = "https://stream.twitter.com/1.1/statuses/sample.json"
    #headeroauth = OAuth1(signature_type='auth_header', **token)
    #while True:
        #r = req.get(url, auth=headeroauth, timeout=90.0, stream=True)
        #if r.status_code == 200:
            #count[0] = 1
            #httpcount[0] = 1
            #for tweet in r.iter_lines():
                #if tweet:
                    #yield tweet
        #if r.status_code == 420:
            #stream_rate_limit(r, count)
        #else:
            #stream_rate_limit(r, httpcount)
        #continue

    #raise SystemExit()

def user_timeline(user_id, auth):
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

#def users_show(user_id, token):
    #"""
    #Get the profile of the given of the given user.

    #user_id - A user_id of a single twitter user.
    #return  - A 2 tuple. First is the status code returned by Twitter, second is
              #the profile of the Twitter user. If status code is 403 or 403, the
              #profile will instead contain the reason of absence of the profile.
    #"""

    #url = "http://api.twitter.com/1.1/users/show.json"
    #params = {
        #"user_id": user_id,
        #"include_entities": 1
    #}

    #headeroauth = OAuth1( signature_type='auth_header', **token)
    #tries = 0
    #while tries < MAX_RETRY:
        #r = req.get(url, params=params, auth=headeroauth, timeout=60.0)

        ## Proper receive
        #if r.status_code == 200:
            #check_rate_limit(r)
            #return (200, r.json())

        ## User doesn't exist
        #if r.status_code in (403, 404):
            #check_rate_limit(r)
            #return (r.status_code, r.json())

        ## Check if rate limited
        #if r.status_code == 400:
            #log.info(u"Try {}: Being throttled - {} {}",
                     #tries, r.status_code, r.text)
            #check_rate_limit(r)
            #tries += 1
            #continue

        ## Dont expect anything else
        #log.warn(u"Try {}: Unexepectd response - {} {}",
                 #tries, r.status_code, r.text)
        #check_rate_limit(r)
        #tries += 1
        #continue

    #log.critical("Maximum retries exhausted ...")
    #raise SystemExit()

