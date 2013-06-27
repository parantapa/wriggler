"""
Test the user_timeline api.
"""

import twitter
from testauth import token

def main():
    """
    Test the user timeline method.
    """

    user_id = 10778222
    tweets = twitter.user_timeline(user_id, token)

    for tweet in tweets:
        print u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])

if __name__ == "__main__":
    main()

