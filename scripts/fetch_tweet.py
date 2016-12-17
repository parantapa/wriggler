#!/usr/bin/env python2
# encoding: utf-8
"""
Retrieve a single tweet from Twitter.
"""

from __future__ import division, print_function, unicode_literals

__author__ = "Parantapa Bhattachara <pb [at] parantapa [dot] net>"

import sys
import json

import logbook

from wriggler.twitter.auth import read_keys
from wriggler.twitter.rest import statuses_show

def main():
    _, tid = sys.argv
    tid = int(tid)

    kfname = "test_keys-twitter.json"
    auth = read_keys(kfname)

    params = {"id": tid}
    tweet, meta = statuses_show(auth, **params)
    assert meta["code"] == 200

    print(json.dumps(tweet))

if __name__ == '__main__':
    logbook.StderrHandler().push_application()
    main()
