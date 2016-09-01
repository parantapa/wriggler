"""
Robust Twitter crawler primitives.
"""

from wriggler import log, Error
import wriggler.const as const
import wriggler.req as req
import wriggler.twitter.error_codes as ec
from wriggler.twitter import list_to_csv

def rest_call(endpoint, auth, params, method="get"):
    """
    Call a Twitter rest api endpoint.
    """

    ## DEBUG
    # print(endpoint)

    args = {"auth": auth.oauth, "session": auth.session, "timeout": 60.0}

    tries = 0
    while tries < const.API_RETRY_MAX:
        if method == "get":
            r = req.get(endpoint, params=params, **args)
        elif method == "post":
            r = req.post(endpoint, data=params, **args)
        else:
            raise ValueError("Invalid value for parameter 'method'")

        # Proper receive
        if 200 <= r.status_code < 300:
            auth.check_limit(r.headers)

            try:
                data = r.json()
            except ValueError:
                log.info(u"Try L1 {}: Falied to decode JSON - {}\n{}",
                         tries, r.status_code, r.text)
                tries += 1
                continue

            return (data, r.status_code, 0)

        log.info(u"Try L1 {}: Received error", tries)
        todo, status_code, error_code = ec.get_error_todo(r)
        if todo is ec.RETRY:
            auth.check_limit(r.headers)
            tries += 1
            continue
        elif todo is ec.SKIP_AND_RETRY:
            auth.skip_key()
            tries += 1
            continue
        elif todo is ec.GIVEUP:
            try:
                data = r.json()
            except ValueError:
                data = {"response_text": r.text}

            return (data, status_code, error_code)
        else:
            raise RuntimeError("This should not be reached!")

    raise Error("Tries exhausted: %d" % tries)

def id_iter(func, maxitems, auth, params):
    """
    Iterate over the calls of the function using max_id.
    """

    count = 0
    max_id = float("inf")
    while count < maxitems:
        data, meta = func(auth, **params)
        yield data, meta

        if meta["max_id"] is None or meta["max_id"] >= max_id:
            return
        max_id = meta["max_id"]
        count += meta["count"]
        params["max_id"] = meta["max_id"]

def cursor_iter(func, maxitems, auth, params):
    """
    Iteratie over the calls of the function using cursor.
    """

    count = 0
    while count < maxitems:
        data, meta = func(auth, **params)
        yield data, meta

        if meta["next_cursor"] == 0:
            return
        count += meta["count"]
        params["cursor"] = meta["next_cursor"]

def users_show(auth, **params):
    """
    Return the information for a single user.
    """

    endpoint = "https://api.twitter.com/1.1/users/show.json"

    params.setdefault("include_entities", 1)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    return data, {"code": status_code, "error_code": error_code}

def users_lookup(auth, **params):
    """
    Lookup profiles of as many users as possible.
    """

    endpoint = "https://api.twitter.com/1.1/users/lookup.json"

    params.setdefault("include_entities", 1)
    if "user_id" in params:
        params["user_id"] = list_to_csv(params["user_id"])
    if "screen_name" in params:
        params["screen_name"] = list_to_csv(params["screen_name"])

    data, status_code, error_code = rest_call(endpoint, auth, params, method="post")
    return data, {"code": status_code, "error_code": error_code}

def statuses_user_timeline(auth, **params):
    """
    Get the user timeline of a single user.
    """

    maxitems = params.pop("maxitems", 0)
    if maxitems > 0:
        return id_iter(statuses_user_timeline, maxitems, auth, params)

    endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"

    params.setdefault("include_rts", 1)
    params.setdefault("count", 200)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    try:
        max_id = min(tweet["id"] for tweet in data) - 1
        since_id = max(tweet["id"] for tweet in data)
        count = len(data)
    except (ValueError, KeyError, TypeError):
        max_id, since_id, count = None, None, 0

    meta = {
        "code": status_code,
        "error_code": error_code,
        "max_id": max_id,
        "since_id": since_id,
        "count": count,
    }

    return data, meta

def search_tweets(auth, **params):
    """
    Search twitter for tweets.
    """

    maxitems = params.pop("maxitems", 0)
    if maxitems > 0:
        return id_iter(search_tweets, maxitems, auth, params)

    endpoint = 'https://api.twitter.com/1.1/search/tweets.json'

    params.setdefault("count", 100)
    params.setdefault("include_entities", "true")

    data, status_code, error_code = rest_call(endpoint, auth, params)
    try:
        max_id = min(tweet["id"] for tweet in data["statuses"]) - 1
        since_id = min(tweet["id"] for tweet in data["statuses"])
        count = len(data["statuses"])
    except (ValueError, KeyError, TypeError):
        max_id, since_id, count = None, None, 0

    meta = {
        "code": status_code,
        "error_code": error_code,
        "max_id": max_id,
        "since_id": since_id,
        "count": count,
    }

    return data, meta

def friends_ids(auth, **params):
    """
    Get the friend ids of a given user.
    """

    maxitems = params.pop("maxitems", 0)
    if maxitems > 0:
        return cursor_iter(friends_ids, maxitems, auth, params)

    endpoint = "https://api.twitter.com/1.1/friends/ids.json"

    params.setdefault("count", 5000)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    try:
        next_cursor = data["next_cursor"]
        count = len(data["ids"])
    except KeyError:
        next_cursor, count = 0, 0

    meta = {
        "code": status_code,
        "error_code": error_code,
        "next_cursor": next_cursor,
        "count": count,
    }

    return data, meta

def followers_ids(auth, **params):
    """
    Get the friend ids of a given user.
    """

    maxitems = params.pop("maxitems", 0)
    if maxitems > 0:
        return cursor_iter(followers_ids, maxitems, auth, params)

    endpoint = "https://api.twitter.com/1.1/followers/ids.json"

    params.setdefault("count", 5000)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    try:
        next_cursor = data["next_cursor"]
        count = len(data["ids"])
    except KeyError:
        next_cursor, count = 0, 0

    meta = {
        "code": status_code,
        "error_code": error_code,
        "next_cursor": next_cursor,
        "count": count,
    }

    return data, meta

def trends_available(auth):
    """
    Get the list of places for which Twitter has trends.
    """

    endpoint = "https://api.twitter.com/1.1/trends/available.json"
    data, status_code, error_code = rest_call(endpoint, auth, {})
    return data, {"code": status_code, "error_code": error_code}

def trends_place(auth, **params):
    """
    Get the list of trends for the given place.
    """

    endpoint = "https://api.twitter.com/1.1/trends/place.json"
    data, status_code, error_code = rest_call(endpoint, auth, params)
    return data, {"code": status_code, "error_code": error_code}

def favorites_list(auth, **params):
    """
    Get the most recent Tweets liked by the specified user.
    """

    maxitems = params.pop("maxitems", 0)
    if maxitems > 0:
        return id_iter(favorites_list, maxitems, auth, params)

    endpoint = "https://api.twitter.com/1.1/favorites/list.json"

    params.setdefault("include_entities", 1)
    params.setdefault("count", 200)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    try:
        max_id   = min(tweet["id"] for tweet in data) - 1
        since_id = max(tweet["id"] for tweet in data)
        count    = len(data)
    except (ValueError, KeyError, TypeError):
        max_id, since_id, count = None, None, 0

    meta = {
        "code":     status_code,
        "error_code": error_code,
        "max_id":   max_id,
        "since_id": since_id,
        "count":   count,
    }

    return data, meta

def statuses_show(auth, **params):
    """
    Returns a single Tweet, specified by the id parameter.
    """

    endpoint = "https://api.twitter.com/1.1/statuses/show.json"

    params.setdefault("include_entities", 1)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    return data, {"code": status_code, "error_code": error_code}

def statuses_lookup(auth, **params):
    """
    Returns tweet objects for up to 100 tweets per request.
    """

    endpoint = "https://api.twitter.com/1.1/statuses/lookup.json"

    params.setdefault("include_entities", 1)
    params["id"] = list_to_csv(params["id"])

    data, status_code, error_code = rest_call(endpoint, auth, params, method="post")
    return data, {"code": status_code, "error_code": error_code}

def lists_memberships(auth, **params):
    """
    Returns the lists the specified user has been added to.
    """

    maxitems = params.pop("maxitems", 0)
    if maxitems > 0:
        return cursor_iter(lists_memberships, maxitems, auth, params)

    endpoint = "https://api.twitter.com/1.1/lists/memberships.json"

    params.setdefault("count", 1000)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    try:
        next_cursor = data["next_cursor"]
        count = len(data["lists"])
    except KeyError:
        next_cursor, count = 0, 0

    meta = {
        "code": status_code,
        "error_code": error_code,
        "next_cursor": next_cursor,
        "count": count,
    }

    return data, meta

def lists_members(auth, **params):
    """
    Returns the members of the specified list.
    """

    maxitems = params.pop("maxitems", 0)
    if maxitems > 0:
        return cursor_iter(lists_members, maxitems, auth, params)

    endpoint = "https://api.twitter.com/1.1/lists/members.json"

    params.setdefault("include_entities", 1)
    params.setdefault("count", 5000)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    try:
        next_cursor = data["next_cursor"]
        count = len(data["users"])
    except KeyError:
        next_cursor, count = 0, 0

    meta = {
        "code": status_code,
        "error_code": error_code,
        "next_cursor": next_cursor,
        "count": count,
    }

    return data, meta

def lists_show(auth, **params):
    """
    Returns the specified list.
    """

    endpoint = "https://api.twitter.com/1.1/lists/show.json"

    data, status_code, error_code = rest_call(endpoint, auth, params)
    return data, {"code": status_code, "error_code": error_code}

def statuses_retweeters_ids(auth, **params):
    """
    Returns a collection of up to 100 user IDs belonging to users
    who have retweeted the tweet specified by the id parameter.
    """

    maxitems = params.pop("maxitems", 0)
    if maxitems > 0:
        return cursor_iter(statuses_retweeters_ids, maxitems, auth, params)

    endpoint = "https://api.twitter.com/1.1/statuses/retweeters/ids.json"

    params.setdefault("stringify_ids", "false")

    data, status_code, error_code = rest_call(endpoint, auth, params)
    try:
        next_cursor = data["next_cursor"]
        count = len(data["ids"])
    except KeyError:
        next_cursor, count = 0, 0

    meta = {
        "code": status_code,
        "error_code": error_code,
        "next_cursor": next_cursor,
        "count": count,
    }

    return data, meta

def statuses_retweets_id(auth, **params):
    """
    Returns a collection of the 100 most recent retweets
    of the tweet specified by the id parameter.
    """

    endpoint = "https://api.twitter.com/1.1/statuses/retweets/{}.json"

    endpoint = endpoint.format(params.pop("id"))

    params.setdefault("count", 100)

    data, status_code, error_code = rest_call(endpoint, auth, params)
    meta = {"code": status_code, "error_code": error_code}

    return data, meta
