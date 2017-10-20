# Copyright (c) 2012-2017 Snowflake Computing Inc. All rights reserved.
from botocore.vendored.requests import Response


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

        self.code = json_body[u'code']
        self.success = json_body[u'success']
        self._raw_message = json_body[u'message']
        self.data = json_body[u'data']
        self.message = 'Http Error: {}, Vender Code: {}, Message: {}'\
            .format(self.http_error_code, self.code, self._raw_message)

        return

    def __str__(self):
        return self.message
