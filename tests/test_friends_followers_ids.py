"""
Test the users_lookup api.
"""

import sys
sys.path.append(".")

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import twitter
from testauth import token

def main():
    """
    Test the users_lookup method.
    """

    user_id = 478409690

    friends = twitter.friends_ids(user_id, token)
    print len(friends)
    print friends[:5]
    
    followers = twitter.followers_ids(user_id, token)
    print len(followers)
    print followers[:5]

if __name__ == "__main__":
    main()
