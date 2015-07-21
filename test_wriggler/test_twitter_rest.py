# pylint: disable=redefined-outer-name
"""
Test the search_tweets api.
"""

import pytest

import wriggler.twitter.auth as auth
import wriggler.twitter.rest as rest

TEST_USERS = [
    (813286, "BarackObama"),
    (145125358, "SrBachchan")
]

TEST_QUERY = ["news", "ff"]

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

    for user_id, screen_name in TEST_USERS:
        params = {"user_id": user_id}
        profile, meta = rest.users_show(samp_auth, **params)
        assert meta["code"] == 200
        assert profile["id"] == user_id
        assert profile["screen_name"] == screen_name

        params = {"screen_name": screen_name}
        profile, meta = rest.users_show(samp_auth, **params)
        assert meta["code"] == 200
        assert profile["id"] == user_id
        assert profile["screen_name"] == screen_name

def test_users_lookup(samp_auth):
    """
    Test the users_lookup method.
    """

    user_ids = set(u[0] for u in TEST_USERS)
    screen_names = set(u[1] for u in TEST_USERS)

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

    for user_id, screen_name in TEST_USERS:
        params = {"user_id": user_id, "count": 10}
        tweets, meta = rest.statuses_user_timeline(samp_auth, **params)
        assert meta["code"] == 200
        assert all(t["user"]["id"] == user_id for t in tweets)
        assert all(t["user"]["screen_name"] == screen_name for t in tweets)

        params = {"screen_name": screen_name, "count": 10}
        tweets, meta = rest.statuses_user_timeline(samp_auth, **params)
        assert meta["code"] == 200
        assert all(t["user"]["id"] == user_id for t in tweets)
        assert all(t["user"]["screen_name"] == screen_name for t in tweets)

def test_statuses_user_timeline_iter(samp_auth):
    """
    Test the statuses/user_timeline method using id_iter.
    """

    for user_id, screen_name in TEST_USERS:
        params = {"user_id": user_id, "count": 10, "maxitems": 20}
        results = []
        for tweets, meta in rest.statuses_user_timeline(samp_auth, **params):
            assert meta["code"] == 200
            results.extend(tweets)
        assert all(t["user"]["id"] == user_id for t in results)
        assert all(t["user"]["screen_name"] == screen_name for t in results)
        assert len(results) >= 20
        assert len(set(r["id"] for r in results)) >= 20

def test_search_tweets(samp_auth):
    """
    Test the tweets_search method.
    """

    for query in TEST_QUERY:
        params = {"q": query, "result_type": "recent"}
        _, meta = rest.search_tweets(samp_auth, **params)
        assert meta["code"] == 200

def test_search_tweets_iter(samp_auth):
    """
    Test the tweets_search method w/ id_iter.
    """

    for query in TEST_QUERY:
        params = {"q": query, "result_type": "recent", "count": 10,
                  "maxitems": 20}
        results = []
        for data, meta in rest.search_tweets(samp_auth, **params):
            assert meta["code"] == 200
            results.extend(data["statuses"])
        assert len(results) >= 20
        assert len(set(r["id"] for r in results)) >= 20

def test_friends_ids(samp_auth):
    """
    Test friends/ids method.
    """

    for user_id, _ in TEST_USERS:
        params = {"user_id": user_id, "count": 10}
        data, meta = rest.friends_ids(samp_auth, **params)
        assert meta["code"] == 200
        assert len(data["ids"]) >= 10

def test_friends_ids_iter(samp_auth):
    """
    Test friends/ids method w/ cursor_iter.
    """

    for user_id, _ in TEST_USERS:
        params = {"user_id": user_id, "count": 10, "maxitems": 20}
        results = []
        for data, meta in rest.friends_ids(samp_auth, **params):
            assert meta["code"] == 200
            assert len(data["ids"]) >= 10
            results.extend(data["ids"])
        assert len(results) >= 20
        assert len(set(results)) >= 20

def test_followers_ids(samp_auth):
    """
    Test followers/ids method.
    """

    for user_id, _ in TEST_USERS:
        params = {"user_id": user_id, "count": 10}
        data, meta = rest.followers_ids(samp_auth, **params)
        assert meta["code"] == 200
        assert len(data["ids"]) >= 10

def test_followers_ids_iter(samp_auth):
    """
    Test followers/ids method w/ cursor_iter.
    """

    for user_id, _ in TEST_USERS:
        params = {"user_id": user_id, "count": 10, "maxitems": 20}
        results = []
        for data, meta in rest.followers_ids(samp_auth, **params):
            assert meta["code"] == 200
            results.extend(data["ids"])
        assert len(results) >= 20
        assert len(set(results)) >= 20

def test_trends_available(samp_auth):
    """
    Test the trends available api.
    """

    data, meta = rest.trends_available(samp_auth)
    assert meta["code"] == 200
    assert isinstance(data, list)
    assert len(data) > 10
    for place in data:
        assert "woeid" in place

def test_trends_place(samp_auth):
    """
    Test the trends api for places.
    """

    params = {"id": 1}
    data, meta = rest.trends_place(samp_auth, **params)
    assert meta["code"] == 200
    for trend in data:
        for obj in trend["trends"]:
            assert "name" in obj
