"""
Check statuses/sample for streaming api tweets.
"""

import sys
sys.path.append(".")

from itertools import islice

import twitter
from testauth import token

def main():
    """
    Test the statues_sample method.
    """

    for obj in islice(twitter.statuses_sample(token), 100):
        print obj

if __name__ == "__main__":
    main()

