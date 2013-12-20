"""
Test the statuses/user_timeline api
"""

import sys
sys.path.append(".")

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import twitter.auth
from twitter.rest import id_iterator, statuses_user_timeline

def main():
    """
    Test the statuses/user_timeline method.
    """

    kfname = "raw-keys-test.json"
    auth = twitter.auth.read_multi_auth(kfname)

    params = {"user_id": 813286}
    tweets = id_iterator(statuses_user_timeline, 5000, auth, **params)
    for tweet in tweets:
        print u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])

    params = {"screen_name": "BarackObama"}
    tweets = id_iterator(statuses_user_timeline, 5, auth, **params)
    for tweet in tweets:
        print u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])

if __name__ == "__main__":
    main()

