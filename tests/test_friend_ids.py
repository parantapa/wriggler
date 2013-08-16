"""
Test the users_lookup api.
"""

import sys
sys.path.append(".")

import twitter
from testauth import token

def main():
    """
    Test the users_lookup method.
    """

    user_id = 145125358
    friends = twitter.friend_ids(user_id, token)

    print len(friends)
    print friends[:5]

if __name__ == "__main__":
    main()

