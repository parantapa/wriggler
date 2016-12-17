# pylint: disable=bad-continuation
"""
Description of Error codes.

https://dev.twitter.com/overview/api/response-codes
Accessed on: September 01, 2016
"""

import logbook

log = logbook.Logger(__name__)

# Logic on code
RETRY = 1
SKIP_AND_RETRY = 2
GIVEUP = 3

STATUS_CODES = [
    # (200, "OK", 0),
    # Success

    # (304, "Not Modified", 0),
    # There was no new data to return.

    (400, "Bad Request", GIVEUP),
    # The request was invalid or cannot be otherwise served.
    # An accompanying error message will explain further.
    # In API v1.1, requests without authentication are considered invalid
    # and will yield this response.

    (401, "Unauthorized", GIVEUP),
    # Authentication credentials were missing or incorrect.
    # Also returned in other circumstances,
    # for example all calls to API v1 endpoints now return 401
    # (use API v1.1 instead).

    (403, "Forbidden", GIVEUP),
    # The request is understood,
    # but it has been refused or access is not allowed.
    # An accompanying error message will explain why.
    # This code is used when requests are being denied due to update limits.
    # Other reasons for this status being returned are listed
    # alongside the response codes in the table below.

    (404, "Not Found", GIVEUP),
    # The URI requested is invalid or the resource requested,
    # such as a user, does not exists.
    # Also returned when the requested format is not supported
    # by the requested method.

    (406, "Not Acceptable", GIVEUP),
    # Returned by the Search API when an invalid format is specified
    # in the request.

    (410, "Gone", GIVEUP),
    # This resource is gone.
    # Used to indicate that an API endpoint has been turned off.
    # For example: 'The Twitter REST API v1 will soon stop functioning.
    # Please migrate to API v1.1.'

    (420, "Enhance Your Calm", RETRY),
    # Returned by the version 1 Search and Trends APIs
    # when you are being rate limited.

    (422, "Unprocessable Entity", GIVEUP),
    # Returned when an image uploaded to POST account / update_profile_banner
    # is unable to be processed.

    (429, "Too Many Requests", RETRY),
    # Returned in API v1.1 when a request cannot be served
    # due to the application's rate limit
    # having been exhausted for the resource.
    # See Rate Limiting in API v1.1.

    (500, "Internal Server Error", RETRY),
    # Something is broken.
    # Please post to the developer forums so the Twitter team can investigate.

    (502, "Bad Gateway", RETRY),
    # Twitter is down or being upgraded.

    (503, "Service Unavailable", RETRY),
    # The Twitter servers are up, but overloaded with requests. Try again later.

    (504, "Gateway timeout", RETRY)
    # The Twitter servers are up, but the request couldn't be serviced
    # due to some failure within our stack. Try again later.
]

STATUS_CODE_TODO = {code: todo for code, _, todo in STATUS_CODES}

# Code, Text, Logic
ERROR_CODES = [
    (32, "Could not authenticate you", SKIP_AND_RETRY),
    # Your call could not be completed as dialed

    (34, "Sorry, that page does not exist", GIVEUP),
    # Corresponds with an HTTP 404
    # -- the specified resource was not found

    (64, "Your account is suspended and is not permitted to access this feature", SKIP_AND_RETRY),
    # Corresponds with an HTTP 403
    # -- the access token being used belongs to a suspended user
    # and they can't complete the action you're trying to take

    (68, "The Twitter REST API v1 is no longer active.", GIVEUP),
    # Corresponds to a HTTP request to a retired v1-era URL.

    (88, "Rate limit exceeded", RETRY),
    # The request limit for this resource has been reached
    # for the current rate limit window.

    (89, "Invalid or expired token", SKIP_AND_RETRY),
    # The access token used in the request is incorrect
    # or has expired. Used in API v1.1

    (92, "SSL is required", GIVEUP),
    # Only SSL connections are allowed in the API,
    # you should update your request to a secure connection.
    # See how to connect using SSL.

    (130, "Over capacity", RETRY),
    # Corresponds with an HTTP 503
    # -- Twitter is temporarily over capacity.

    (131, "Internal error", RETRY),
    # Corresponds with an HTTP 500
    # -- An unknown internal error occurred.

    (135, "Could not authenticate you", SKIP_AND_RETRY),
    # Corresponds with a HTTP 401
    # -- Your oauth_timestamp is either ahead or behind our acceptable range.

    (136, "You have been blocked from {action}", GIVEUP),
    # Corresponds with a HTTP 401
    # -- The user associated with the action you are performing has blocked you.

    (161, "You are unable to follow more people at this time", GIVEUP),
    # Corresponds with HTTP 403
    # -- thrown when a user cannot follow another user due to some kind of limit.

    (179, "Sorry, you are not authorized to see this status", GIVEUP),
    # Corresponds with HTTP 403
    # -- thrown when a Tweet cannot be viewed
    # by the authenticating user,
    # usually due to the tweet's author having protected their tweets.

    (185, "User is over daily status update limit", GIVEUP),
    # Corresponds with HTTP 403
    # -- thrown when a tweet cannot be posted
    # due to the user having no allowance remaining to post.
    # Despite the text in the error message
    # indicating that this error is only thrown when a daily limit is reached,
    # this error will be thrown whenever a posting limitation has been reached.
    # Posting allowances have roaming windows of time of unspecified duration.

    (187, "Status is a duplicate", GIVEUP),
    # The status text has been Tweeted already by the authenticated account.

    (215, "Bad authentication data",  SKIP_AND_RETRY),
    # Typically sent with 1.1 responses with HTTP code 400.
    # The method requires authentication
    # but it was not presented or was wholly invalid.

    (226, "This request looks like it might be automated. " +
          "To protect our users from spam and other malicious activity, " +
          "we can't complete this action right now.",
          SKIP_AND_RETRY),
    # We constantly monitor and adjust our filters
    # to block spam and malicious activity on the Twitter platform.
    # These systems are tuned in real-time.
    # If you get this response our systems have flagged the Tweet
    # or DM as possibly fitting this profile.
    # If you feel that the Tweet or DM you attempted to create was flagged in error,
    # please report the details around that to us
    # by filing a ticket at https://support.twitter.com/forms/platform.

    (231, "User must verify login", GIVEUP),
    # Returned as a challenge in xAuth
    # when the user has login verification enabled on their account
    # and needs to be directed to twitter.com
    # to generate a temporary password.

    (251, "This endpoint has been retired and should not be used.", GIVEUP),
    # Corresponds to a HTTP request to a retired URL.

    (261, "Application cannot perform write actions.", GIVEUP),
    # Corresponds with HTTP 403
    # -- thrown when the application is restricted
    # from POST, PUT, or DELETE actions.
    # See How to appeal application suspension and other disciplinary actions.

    (271, "You can't mute yourself", GIVEUP),
    # Corresponds with HTTP 403.
    # The authenticated user account cannot mute itself.

    (272, "You are not muting the specified user", GIVEUP),
    # Corresponds with HTTP 403.
    # The authenticated user account is not muting the account
    # a call is attempting to unmute.

    (326, "To protect our users from spam and other malicious activity, " +
          "this account is temporarily locked. " +
          "Please log in to https://twitter.com to unlock your account.",
          SKIP_AND_RETRY),
    # NOTE: As of September 01, 2016 this error was not listed on
    # https://dev.twitter.com/overview/api/response-codes

    (354, "The text of your direct message is over the max character limit.", GIVEUP),
    # Corresponds with HTTP 403.
    # The message size exceeds the number of characters
    # permitted in a direct message.

]

ERROR_CODE_TODO = {code: todo for code, _, todo in ERROR_CODES}

def get_error_todo(response):
    """
    Decide what to do.
    """

    status_code = response.status_code
    assert not 200 <= status_code < 300

    try:
        error = response.json()
        error_code = error["errors"][0]["code"]
        error_msg = error["errors"][0]["message"]
        logfn = log.debug
    except (ValueError, KeyError, IndexError):
        error_code = 0
        error_msg = response.text
        logfn = log.notice

    if error_code in ERROR_CODE_TODO:
        todo = ERROR_CODE_TODO[error_code]
    elif status_code in STATUS_CODE_TODO:
        todo = STATUS_CODE_TODO[status_code]
    elif 500 <= status_code < 600:
        todo = RETRY
    else:
        todo = GIVEUP

    todo_text = {RETRY: "retry",
                 SKIP_AND_RETRY: "skip_and_retry",
                 GIVEUP: "giveup"}[todo]

    hline = u"-" * 80
    fmt = u"status_code: {}, error_code: {}, logic: {}\n{}\n{}\n{}".format
    msg = fmt(status_code, error_code, todo_text, hline, error_msg, hline)
    logfn(msg)

    return todo, status_code, error_code
