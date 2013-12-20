"""
Runtime constants.
"""

# Wait for this many seconds after the start of new rate limit window.
RATE_LIMIT_RESET_BUFFER = 5

# Stop making requests when this many requests is allowed
RATE_LIMIT_BUFFER = 1

# In case of unknown error retry after this many seconds
RETRY_AFTER = 5

# The rate limit time window as set by Twitter = 15 minutes
WINDOW_TIME = 15 * 60

# If requests keep failing for 4 hours give up
GIVE_UP_AFTER = 4 * 60 * 60

# Maximum number of retries
RETRY_MAX = GIVE_UP_AFTER // RETRY_AFTER

