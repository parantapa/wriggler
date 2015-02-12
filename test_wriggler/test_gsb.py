"""
Test the Google safebrowsing api
"""

import pytest

import wriggler.gsb as gsb

URLS = [
        "http://slashdot.org",
        "http://news.ycombinator.com",
        "http://reddit.com"
]

@pytest.fixture
def samp_key():
    """
    Return the sample auth object.
    """

    kfname = "gsb-test-key.txt"
    with open(kfname, "r") as fobj:
        key = fobj.read().strip()
    return key

def test_lookup(samp_key):
    """
    Test the google safe browsing lookup function.
    """

    for response, status_code in gsb.lookup(samp_key, URLS):
        assert status_code in (200, 204)
        for u in URLS:
            assert response[u] in ("phishing", "malware", "phishing,malware", "ok")

