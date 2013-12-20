"""
Test the search_tweets api.
"""

import pytest

import twitter.auth as auth
import twitter.rest as rest

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

    params = {"user_id": 813286}
    profile, meta = rest.users_show(samp_auth, **params)
    assert meta["code"] == 200
    assert profile["id"] == 813286
    assert profile["screen_name"] == "BarackObama"

    params = {"screen_name": "BarackObama"}
    profile, meta = rest.users_show(samp_auth, **params)
    assert meta["code"] == 200
    assert profile["id"] == 813286
    assert profile["screen_name"] == "BarackObama"

def test_users_lookup(samp_auth):
    """
    Test the users_lookup method.
    """

    user_ids = set([813286, 145125358])
    screen_names = set(["BarackObama", "SrBachchan"])

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

