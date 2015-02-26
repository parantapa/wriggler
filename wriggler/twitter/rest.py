"""
Robust Twitter crawler primitives.
"""

from requests_oauthlib import OAuth1

from wriggler import log, Error
import wriggler.const as const
import wriggler.req as req
import wriggler.twitter.error_codes as ec

def list_to_csv(args):
    """
    Convert a list to a string csv.
    """

    args = map(str, args)
    args = ",".join(args)
    return args

class TwitterRestAPIError(Error):
    """
    The Twitter API returned an error.
    """

    def __init__(self, response):
        super(TwitterRestAPIError, self).__init__(response)

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
        fmt = "TwitterRestAPIError(http_status_code={0},error_code={1})"
        return fmt.format(self.http_status_code, self.error_code)

    def __str__(self):
        htext, hdesc = ec.HTTP_STATUS_CODES.get(self.http_status_code,
                                                ("Unknown", "Unknown"))
        etext, edesc = ec.ERROR_CODES.get(self.error_code,
                                          ("Unknown", "Unknown"))
        body = unicode(self.body).encode("utf-8")

        hdr = "TwitterRestAPIError\nhttp_status_code: {0} - {1}\n{2}\nerror_code: {3} - {4}\n{5}"
        hdr = hdr.format(self.http_status_code, htext, hdesc,
                         self.error_code, etext, edesc)
        return hdr + "\n--------\n" + body

def id_iter(func, maxitems, auth, **params):
    """
    Iterate over the calls of the function using max_id
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

def cursor_iter(func, maxitems, auth, **params):
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

def twitter_rest_call(endpoint, auth, accept_codes, params, method="get"):
    """
    Call a Twitter rest api endpoint.
    """

    ## DEBUG
    # print(endpoint)

    token = auth.get_token()
    oauth = OAuth1(signature_type="auth_header", **token)

    tries = 0
    while tries < const.API_RETRY_MAX:
        if method == "get":
            r = req.get(endpoint, params=params, auth=oauth, timeout=60.0)
        elif method == "post":
            r = req.post(endpoint, data=params, auth=oauth, timeout=60.0)
        else:
            raise ValueError("Invalid value for parameter 'method'")

        # Proper receive
        if 200 <= r.status_code < 300 or r.status_code in accept_codes:
            auth.check_limit(r.headers)

            try:
                data = r.json()
            except ValueError:
                log.info(u"Try L1 {}: Falied to decode Json - {} {}",
                         tries, r.status_code, r.text)
                tries += 1
                continue

            return (data, r.status_code)

        # Check if rate limited
        if r.status_code in (431, 429):
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
    raise TwitterRestAPIError(r)

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

    data, code = twitter_rest_call(endpoint, auth, accept_codes, params, method="post")
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
    except (ValueError, KeyError, TypeError):
        max_id, since_id, count = None, None, 0

    meta = {
        "code": code,
        "max_id": max_id,
        "since_id": since_id,
        "count": count,
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
    except (ValueError, KeyError, TypeError):
        max_id, since_id, count = None, None, 0

    meta = {
        "code": code,
        "max_id": max_id,
        "since_id": since_id,
        "count": count,
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
    }

    return data, meta
