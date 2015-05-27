# encoding: utf-8
"""
APIs for services in azure datamarket.
"""

from wriggler import Error

class AzureError(Error):
    """
    Error returned by azure datamarket service.
    """

    def __init__(self, response, tries):
        super(AzureError, self).__init__(response, tries)

        self.response = response
        self.tries = tries

        self.http_status_code = response.status_code
        self.body = response.text

    def __repr__(self):
        fmt = "AzureError(http_status_code={0})"
        return fmt.format(self.http_status_code)

    def __str__(self):
        fmt = ("AzureError\n"
               "http_status_code: {0}\n"
               "--------\n{1}")
        return fmt.format(self.http_status_code, self.text)
