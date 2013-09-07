"""
Test the user_timeline api.
"""

import sys
sys.path.append(".")

import twitter
from testauth import token

def main():
    """
    Test the user timeline method.
    """

    user_id = 813286
    tweets = twitter.user_timeline(user_id, token)

    for tweet in tweets:
        line = u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])
        print line.encode("utf-8")

if __name__ == "__main__":
    main()

