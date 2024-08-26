# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
from requests import Response

class IngestResponseError(Exception):
    """
        Error thrown when rest request failed
    """
    def __init__(self, response: Response):
        self.http_error_code = response.status_code

        try:
            json_body = response.json()
        except ValueError:
            self.message = 'Http Error: {}, Message: {}'.format(self.http_error_code,
                                                                response.reason)
            return

        try:
            self.code = json_body[u'code']
            self.success = json_body[u'success']
            self._raw_message = json_body[u'message']
            self.data = json_body[u'data']
            self.message = 'Http Error: {}, Vender Code: {}, Message: {}' \
                .format(self.http_error_code, self.code, self._raw_message)
        except KeyError:
            self.message = 'Http Error: {}, Message: {}, Body: {}'.format(self.http_error_code,
                                                                          response.reason,
                                                                          json_body)
        return

    def __str__(self):
        return self.message


class IngestClientError(Exception):
    """
        Error thrown in the client side
    """
    def __init__(self, **kwargs):
        self.code = kwargs.get('code')
        self.message = kwargs.get('message')

    def __str__(self):
        return 'Vendor Code: {}, Message: {}'\
            .format(self.code, self.message)
