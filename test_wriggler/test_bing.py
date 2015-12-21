"""
Test the Bing Search API
"""

import json
import pytest
import wriggler.azure.bing as bing

QUERIES = [
    "google",
    "yahoo"
]

CHECK_KEYS = [
    "Title",
    "Description",
    "Url",
    "ID"
]

@pytest.fixture
def samp_key():
    """
    Return the sample auth object.
    """

    kfname = "test_key-azure.txt"
    with open(kfname) as fobj:
        key = fobj.read().strip()

    return key

# pylint: disable=redefined-outer-name
def test_search(samp_key):
    """
    Test the bing search api.
    """

    for query in QUERIES:
        r, code = bing.search(samp_key, query)
        assert code == 200
        assert len(r["d"]["results"]) > 0

        for key in CHECK_KEYS:
            for x in r["d"]["results"]:
                assert key in x
