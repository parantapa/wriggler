"""
Test the search_tweets api.
"""

import pytest

import twitter.auth as auth
import twitter.rest as rest

U = [
    (813286, "BarackObama"),
    (145125358, "SrBachchan")
]

@pytest.fixture
def samp_auth():
    """
    Return the sample auth object.
    """

    kfname = "raw-keys-test.json"
    ath = auth.read_multi_auth(kfname)
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

    params = {"user_id": U[0][0]}
    tweets, meta = rest.statuses_user_timeline(samp_auth, **params)
    assert meta["code"] == 200
    assert all(t["user"]["id"] == U[0][0] for t in tweets)
    assert all(t["user"]["screen_name"] == U[0][1] for t in tweets)

    params = {"screen_name": U[0][1]}
    tweets, meta = rest.statuses_user_timeline(samp_auth, **params)
    assert meta["code"] == 200
    assert all(t["user"]["id"] == U[0][0] for t in tweets)
    assert all(t["user"]["screen_name"] == U[0][1] for t in tweets)

