"""
Test the search_tweets api.
"""

import sys
sys.path.append(".")

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import twitter.auth
from twitter.rest import id_iterator, search_tweets

def main():
    """
    Test the tweets_search method.
    """

    kfname = "raw-keys-test.json"
    auth = twitter.auth.read_multi_auth(kfname)

    params = {"q": "#congress", "result_type": "recent"}
    tweets = id_iterator(search_tweets, 10, auth, **params)

    for tweet in tweets:
        print u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])

if __name__ == "__main__":
    main()

