"""
Test the user_show api.
"""

import sys
sys.path.append(".")

import twitter
from testauth import token

def main():
    """
    Test the users_show method.
    """

    user_id = 813286
    status, profile = twitter.user_show(user_id, token)

    print status
    print profile

if __name__ == "__main__":
    main()

