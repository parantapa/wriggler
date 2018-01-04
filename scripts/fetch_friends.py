#!/usr/bin/env python2
# encoding: utf-8
"""
Retrieve a single profile from Twitter.
"""

from __future__ import division, print_function, unicode_literals

__author__ = "Parantapa Bhattachara <pb [at] parantapa [dot] net>"

import sys
import json

import logbook

from wriggler.twitter.auth import read_keys
from wriggler.twitter.rest import friends_ids, users_lookup

def main():
    _, user = sys.argv

    try:
        params = {"id": int(user)}
    except ValueError:
        params = {"screen_name": user}

    kfname = "test_keys-twitter.json"
    auth = read_keys(kfname)

    data, meta = friends_ids(auth, **params)
    assert meta["code"] == 200

    print(json.dumps(data))

if __name__ == '__main__':
    logbook.StderrHandler().push_application()
    main()
