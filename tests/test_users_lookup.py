"""
Test the users_lookup api.
"""

import sys
sys.path.append(".")

import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout)

import twitter.auth
import twitter.rest

def main():
    """
    Test the users_lookup method.
    """

    kfname = "raw-keys-test.json"
    auth = twitter.auth.read_multi_auth(kfname)

    params = {"user_id": [813286, 145125358]}
    profiles, _ = twitter.rest.users_lookup(auth, **params)
    for profile in profiles:
        print u"@{screen_name} - {name} - {description}".format(**profile)

    params = {"screen_name": ["BarackObama", "SrBachchan"]}
    profiles, _ = twitter.rest.users_lookup(auth, **params)
    for profile in profiles:
        print u"@{screen_name} - {name} - {description}".format(**profile)

if __name__ == "__main__":
    main()

