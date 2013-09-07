"""
Test the user_timeline api.
"""

import sys
sys.path.append(".")

import twitter
from testauth import token

def main():
    """
    Test the tweets_search method.
    """

    query = "#bpl"
    result_type = "recent"
    tweets = twitter.search_tweets(query, result_type, token, 100)

    for tweet in tweets:
        print u"@{} - {}".format(tweet["user"]["screen_name"], tweet["text"])

if __name__ == "__main__":
    main()

