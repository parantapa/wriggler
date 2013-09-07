"""
Check statuses/sample for streaming api tweets.
"""

import sys
sys.path.append(".")

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

from itertools import islice

import twitter
from testauth import token

def main():
    """
    Test the statues_sample method.
    """

    tweets = islice(twitter.statuses_sample(token), 10000)

    for tweet in tweets:
        if "text" in tweet and "user" in tweet:
            print u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])

if __name__ == "__main__":
    main()

