"""
Robust Twitter crawler primitives.
"""

from requests_oauthlib import OAuth1

from twitter import log, Error
import twitter.const as const
import twitter.req as req
from twitter.error_codes import HTTP_STATUS_CODES, ERROR_CODES

def list_to_csv(args):
    """
    Convert a list to a string csv.
    """

    args = map(str, args)
    args = ",".join(args)
    return args

class APIError(Error):
    """
    The Twitter API returned an error.
    """

    def __init__(self, response):
        super(APIError, self).__init__(response)

        self.response = response

        self.http_status_code = response.status_code
        try:
            self.body = response.json()
            self.parsed_body = True
        except ValueError:
            self.body = response.text
            self.parsed_body = False

        if self.parsed_body:
            try:
                self.error_code = self.body["errors"][0]["code"]
            except (KeyError, IndexError):
                self.error_code = None
        else:
            self.error_code = None

    def __repr__(self):
        fmt = "APIError(http_status_code={0},error_code={1})"
        return fmt.format(self.http_status_code, self.error_code)

    def __str__(self):
        htext, hdesc = HTTP_STATUS_CODES.get(self.http_status_code,
                                             ("Unknown", "Unknown"))
        etext, edesc = ERROR_CODES.get(self.error_code,
                                       ("Unknown", "Unknown"))
        body = unicode(self.body).encode("utf-8")

        hdr = "APIError\nhttp_status_code: {0} - {1}\n{2}\nerror_code: {3} - {4}\n{5}"
        hdr = hdr.format(self.http_status_code, htext, hdesc,
                         self.error_code, etext, edesc)
        return hdr + "\n--------\n" + body

def id_iter(func, maxitems, auth, **params):
    """
    Iterate over the calls of the function using max_id
    """

    count = 0
    while count < maxitems:
        data, meta = func(auth, **params)
        yield data, meta

        if meta["max_id"] is None or meta["finished"]:
            return
        count += meta["count"]
        params["max_id"] = meta["max_id"]

def cursor_iter(func, maxitems, auth, **params):
    """
    Iteratie over the calls of the function using cursor.
    """

    count = 0
    while count < maxitems:
        data, meta = func(auth, **params)
        yield data, meta

        if meta["next_cursor"] == 0 or meta["finished"]:
            return
        count += meta["count"]
        params["cursor"] = meta["next_cursor"]

def twitter_rest_call(endpoint, auth, accept_codes, params):
    """
    Call a Twitter rest api endpoint.
    """

    token = auth.get_token()
    oauth = OAuth1(signature_type="auth_header", **token)

    tries = 0
    while tries < const.RETRY_MAX:
        r = req.get(endpoint, params=params, auth=oauth, timeout=60.0)

        # Proper receive
        if 200 <= r.status_code < 300 or r.status_code in accept_codes:
            auth.check_limit(r.headers)
            return (r.json(), r.status_code)

        # Check if rate limited
        if r.status_code == 429:
            log.info(u"Try L1 {}: Being throttled - {} {}",
                     tries, r.status_code, r.text)
            auth.check_limit(r.headers)
            tries += 1
            continue

        # Server side error; Retry after delay
        if 500 <= r.status_code < 600:
            log.info(u"Try L1 {}: Server side error {} {}",
                     tries, r.status_code, r.text)
            auth.check_limit(r.headers)
            tries += 1

        # Some other error; Break out of loop
        break

    log.error(u"Try L1 {}: Unexepectd response - {} {}",
              tries, r.status_code, r.text)
    raise APIError(r)

def users_show(auth, **params):
    """
    Return the information for a single user.
    """

    endpoint = "https://api.twitter.com/1.1/users/show.json"
    accept_codes = (403, 404)

    params.setdefault("include_entities", 1)

    data, code = twitter_rest_call(endpoint, auth, accept_codes, params)
    return data, {"code": code}

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

    data, code = twitter_rest_call(endpoint, auth, accept_codes, params)
    return data, {"code": code}

def statuses_user_timeline(auth, **params):
    """
    Get the user timeline of a single user.
    """

    endpoint = "https://api.twitter.com/1.1/statuses/user_timeline.json"
    accept_codes = (403, 404)

    params.setdefault("include_rts", 1)
    params.setdefault("count", 200)

    data, code = twitter_rest_call(endpoint, auth, accept_codes, params)
    try:
        max_id = min(tweet["id"] for tweet in data) - 1
        since_id = max(tweet["id"] for tweet in data)
        count = len(data)
    except (ValueError, KeyError):
        max_id, since_id, count = None, None, 0

    meta = {
        "code": code,
        "max_id": max_id,
        "since_id": since_id,
        "count": count,
        "finished": count < params["count"]
    }

    return data, meta

def search_tweets(auth, **params):
    """
    Search twitter for tweets.
    """

    endpoint = 'https://api.twitter.com/1.1/search/tweets.json'
    accept_codes = ()

    params.setdefault("count", 100)
    params.setdefault("include_entities", "true")

    data, code = twitter_rest_call(endpoint, auth, accept_codes, params)
    try:
        max_id = min(tweet["id"] for tweet in data["statuses"]) - 1
        since_id = min(tweet["id"] for tweet in data["statuses"])
        count = len(data["statuses"])
    except (ValueError, KeyError):
        max_id, since_id, count = None, None, 0

    meta = {
        "code": code,
        "max_id": max_id,
        "since_id": since_id,
        "count": count,
        "finished": count < params["count"]
    }

    return data, meta

def friends_ids(auth, **params):
    """
    Get the friend ids of a given user.
    """

    endpoint = "https://api.twitter.com/1.1/friends/ids.json"
    accept_codes = (403, 404)

    params.setdefault("count", 5000)

    data, code = twitter_rest_call(endpoint, auth, accept_codes, params)
    try:
        next_cursor = data["next_cursor"]
        count = len(data["ids"])
    except KeyError:
        next_cursor, count = 0, 0

    meta = {
        "code": code,
        "next_cursor": next_cursor,
        "count": count,
        "finished": count < params["count"]
    }

    return data, meta

def followers_ids(auth, **params):
    """
    Get the friend ids of a given user.
    """

    endpoint = "https://api.twitter.com/1.1/followers/ids.json"
    accept_codes = (403, 404)

    params.setdefault("count", 5000)

    data, code = twitter_rest_call(endpoint, auth, accept_codes, params)
    try:
        next_cursor = data["next_cursor"]
        count = len(data["ids"])
    except KeyError:
        next_cursor, count = 0, 0

    meta = {
        "code": code,
        "next_cursor": next_cursor,
        "count": count,
        "finished": count < params["count"]
    }

    return data, meta
