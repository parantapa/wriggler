#!/usr/bin/env python2
# encoding: utf-8
"""
Retrieve a single profile from Twitter.
"""

from __future__ import division, print_function, unicode_literals

__author__ = "Parantapa Bhattachara <pb [at] parantapa [dot] net>"

import sys
import json

from wriggler.twitter.auth import read_keys
from wriggler.twitter.rest import users_show

def main():
    _, user = sys.argv

    try:
        params = {"id": int(user)}
    except ValueError:
        params = {"screen_name": user}

    kfname = "test_keys-twitter.json"
    auth = read_keys(kfname)

    profile, meta = users_show(auth, **params)
    assert meta["code"] == 200

    print(json.dumps(profile))

if __name__ == '__main__':
    main()
