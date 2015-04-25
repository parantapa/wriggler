"""
Runtime constants.
"""

# Retry on connection fail (seconds)
CONNECT_RETRY_AFTER = 10

# Maximum number of connection retries
CONNECT_RETRY_MAX = 10

# In case of unknown error in api, retry after this many seconds
API_RETRY_AFTER = 5

# Maximum number of api retries
API_RETRY_MAX = 10

# Twitter Sepcific Constants
############################

# Wait for this many seconds after the start of new rate limit window.
TWITTER_RATE_LIMIT_RESET_BUFFER = 5

# Stop making requests when this many requests is allowed
TWITTER_RATE_LIMIT_BUFFER = 1

# The rate limit time window as set by Twitter = 15 minutes
TWITTER_DEFAULT_WINDOW_TIME = 15 * 60

