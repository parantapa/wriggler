"""
Runtime constants.
"""

# Wait for this many seconds after the start of new rate limit window.
RATE_LIMIT_RESET_BUFFER = 5

# Stop making requests when this many requests is allowed
RATE_LIMIT_BUFFER = 1

# The rate limit time window as set by Twitter = 15 minutes
WINDOW_TIME = 15 * 60

# Retry on connection fail (seconds)
CONNECT_RETRY_AFTER = 10

# Maximum number of connection retries
CONNECT_RETRY_MAX = 10

# In case of unknown error in rest api, retry after this many seconds
REST_RETRY_AFTER = 5

# Maximum number of retries
RETRY_MAX = 10

