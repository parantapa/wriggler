"""
Test the search_tweets api.
"""

from itertools import islice

import pytest

import wriggler.twitter.auth as auth
import wriggler.twitter.stream as stream

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

    kfname = "test_keys-twitter.json"
    ath = auth.read_keys(kfname)
    return ath

def test_statuses_filter_follow(samp_auth):
    """
    Run statuses filter with follow ids.
    """

    follow = [uid for uid, _ in TEST_USERS]

    iterable = stream.statuses_filter(samp_auth, follow=follow)
    iterable = islice(iterable, 1)
    for line in iterable:
        pass

def test_statuses_filter_track(samp_auth):
    """
    Run statuses filter with track keywords.
    """

    track = TEST_QUERY

    iterable = stream.statuses_filter(samp_auth, track=track)
    iterable = islice(iterable, 5)
    for line in iterable:
        pass

def test_statuses_sample(samp_auth):
    """
    Get 100 lines from statuses sample.
    """

    iterable = stream.statuses_sample(samp_auth)
    iterable = islice(iterable, 100)
    for line in iterable:
        pass


