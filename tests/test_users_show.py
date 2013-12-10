"""
Test the user_show api.
"""

import sys
sys.path.append(".")

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import twitter.auth
import twitter.rest

def main():
    """
    Test the users_show method.
    """

    kfname = "raw-keys-test.json"
    auth = twitter.auth.read_multi_auth(kfname)

    params = {"user_id": 813286}
    profile, status = twitter.rest.users_show(auth, **params)
    print status, profile["name"], "@" + profile["screen_name"]

    params = {"screen_name": "BarackObama"}
    profile, status = twitter.rest.users_show(auth, **params)
    print status, profile["name"], "@" + profile["screen_name"]

if __name__ == "__main__":
    main()

