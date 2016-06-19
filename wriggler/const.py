"""
Runtime constants.
"""

# Retry on connection fail (seconds)
CONNECT_RETRY_AFTER = 1

# Maximum number of connection retries
CONNECT_RETRY_MAX = 1

# In case of unknown error in api, retry after this many seconds
API_RETRY_AFTER = 1

# Maximum number of api retries
API_RETRY_MAX = 1

# In case ratelimit is hit, wake 5 secs after the reset time is over.
API_RESET_BUFFER = 1

