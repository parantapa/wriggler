"""
Test the Foursquare API
"""

import json
import pytest
import wriggler.foursquare as fsq

LOCATIONS = [
    "22.3193,87.3099", # IIT Kharagpur
    "44.3,37.2", # Chicago, IL
]

CHECK_KEYS = [
    "headerLocationGranularity",
    "headerLocation",
    "headerFullLocation",
    "groups"
]

@pytest.fixture
def samp_key():
    """
    Return the sample auth object.
    """

    kfname = "test_key-fsq.json"
    with open(kfname) as fobj:
        key = json.load(fobj)

    return key

# pylint: disable=redefined-outer-name
def test_lookup(samp_key):
    """
    Test the google safe browsing lookup function.
    """

    for location in LOCATIONS:
        params = {"ll": location}
        results, code = fsq.venues_explore(samp_key, **params)
        assert code == 200
        assert results["meta"]["code"] == 200

        for key in CHECK_KEYS:
            assert key in results["response"]
        assert len(results["response"]["groups"]) > 0
