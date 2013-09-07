"""
Test the user_timeline api.
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
    Test the user timeline method.
    """

    user_id = 813286
    tweets = twitter.user_timeline(user_id, auth=token)
    for tweet in islice(tweets, 5):
        print u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])

    screen_name = "BarackObama"
    tweets = twitter.user_timeline(screen_name=screen_name, auth=token)
    for tweet in islice(tweets, 5):
        print u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])

if __name__ == "__main__":
    main()

