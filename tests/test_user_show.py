"""
Test the user_show api.
"""

import sys
sys.path.append(".")

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import twitter
from testauth import token

def main():
    """
    Test the users_show method.
    """

    user_id = 813286
    status, profile = twitter.user_show(user_id, auth=token)
    print status, profile["name"], "@" + profile["screen_name"]

    screen_name = "BarackObama"
    status, profile = twitter.user_show(screen_name=screen_name, auth=token)
    print status, profile["name"], "@" + profile["screen_name"]

if __name__ == "__main__":
    main()

