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

    user_ids = [813286, 145125358]
    profiles = twitter.users_lookup(user_ids, token)

    for profile in profiles:
        print u"@{screen_name} - {name} - {description}".format(**profile)

if __name__ == "__main__":
    main()

