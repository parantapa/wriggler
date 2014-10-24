"""
Test the search_tweets api.
"""

import pytest

import wriggler.twitter.auth as auth
import wriggler.twitter.rest as rest

U = [
    (813286, "BarackObama"),
    (145125358, "SrBachchan")
]

@pytest.fixture
def samp_auth():
    """
    Return the sample auth object.
    """

    kfname = "twitter-test-keys.json"
    ath = auth.read_keys(kfname)
    return ath

def test_users_show(samp_auth):
    """
    Test the users_show method.
    """

    params = {"user_id": U[0][0]}
    profile, meta = rest.users_show(samp_auth, **params)
    assert meta["code"] == 200
    assert profile["id"] == U[0][0]
    assert profile["screen_name"] == U[0][1]

    params = {"screen_name": U[0][1]}
    profile, meta = rest.users_show(samp_auth, **params)
    assert meta["code"] == 200
    assert profile["id"] == U[0][0]
    assert profile["screen_name"] == U[0][1]

def test_users_lookup(samp_auth):
    """
    Test the users_lookup method.
    """

    user_ids = set(u[0] for u in U)
    screen_names = set(u[1] for u in U)

    params = {"user_id": list(user_ids)}
    profiles, meta = rest.users_lookup(samp_auth, **params)
    assert meta["code"] == 200
    assert user_ids == set(p["id"] for p in profiles)
    assert screen_names == set(p["screen_name"] for p in profiles)

    params = {"screen_name": list(screen_names)}
    profiles, meta = rest.users_lookup(samp_auth, **params)
    assert meta["code"] == 200
    assert user_ids == set(p["id"] for p in profiles)
    assert screen_names == set(p["screen_name"] for p in profiles)

def test_statuses_user_timeline(samp_auth):
    """
    Test the statuses/user_timeline method.
    """

    params = {"user_id": U[0][0], "count": 10}
    tweets, meta = rest.statuses_user_timeline(samp_auth, **params)
    assert meta["code"] == 200
    assert all(t["user"]["id"] == U[0][0] for t in tweets)
    assert all(t["user"]["screen_name"] == U[0][1] for t in tweets)

    params = {"screen_name": U[0][1], "count": 10}
    tweets, meta = rest.statuses_user_timeline(samp_auth, **params)
    assert meta["code"] == 200
    assert all(t["user"]["id"] == U[0][0] for t in tweets)
    assert all(t["user"]["screen_name"] == U[0][1] for t in tweets)

def test_statuses_user_timeline_iter(samp_auth):
    """
    Test the statuses/user_timeline method using id_iter.
    """

    params = {"user_id": U[0][0], "count": 10}
    results = []
    for tweets, meta in rest.id_iter(rest.statuses_user_timeline, 20, samp_auth,
                                    **params):
        assert meta["code"] == 200
        results.extend(tweets)
    assert all(t["user"]["id"] == U[0][0] for t in results)
    assert all(t["user"]["screen_name"] == U[0][1] for t in results)
    assert len(results) == 20
    assert len(set(r["id"] for r in results)) == 20

def test_search_tweets(samp_auth):
    """
    Test the tweets_search method.
    """

    query = "news"

    params = {"q": query, "result_type": "recent"}
    tweets, meta = rest.search_tweets(samp_auth, **params)
    assert meta["code"] == 200

def test_search_tweets_iter(samp_auth):
    """
    Test the tweets_search method w/ id_iter.
    """

    query = "news"

    params = {"q": query, "result_type": "recent", "count": 10}
    results = []
    for data, meta in rest.id_iter(rest.search_tweets, 20, samp_auth, **params):
        assert meta["code"] == 200
        results.extend(data["statuses"])
    assert len(results) == 20
    assert len(set(r["id"] for r in results)) == 20

def test_friends_ids(samp_auth):
    """
    Test friends/ids method.
    """

    params = {"user_id": U[0][0], "count": 10}
    data, meta = rest.friends_ids(samp_auth, **params)
    assert meta["code"] == 200
    assert len(data["ids"]) == 10

def test_friends_ids_iter(samp_auth):
    """
    Test friends/ids method w/ cursor_iter.
    """

    params = {"user_id": U[0][0], "count": 10}
    results = []
    for data, meta in rest.cursor_iter(rest.friends_ids, 20, samp_auth,
                                       **params):
        assert meta["code"] == 200
        assert len(data["ids"]) == 10
        results.extend(data["ids"])
    assert len(results) == 20
    assert len(set(results)) == 20

def test_followers_ids(samp_auth):
    """
    Test followers/ids method.
    """

    params = {"user_id": U[0][0], "count": 10}
    data, meta = rest.followers_ids(samp_auth, **params)
    assert meta["code"] == 200
    assert len(data["ids"]) == 10

def test_followers_ids_iter(samp_auth):
    """
    Test followers/ids method w/ cursor_iter.
    """

    params = {"user_id": U[0][0], "count": 10}
    results = []
    for data, meta in rest.cursor_iter(rest.followers_ids, 20, samp_auth,
                                       **params):
        assert meta["code"] == 200
        results.extend(data["ids"])
    assert len(results) == 20
    assert len(set(results)) == 20

