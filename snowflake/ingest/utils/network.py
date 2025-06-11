# import python connector to inject ocsp check method into requests library
import snowflake.connector
import requests
from requests import Response
import time
from ..error import IngestResponseError

from logging import getLogger
logger = getLogger(__name__)

from typing import Dict, Any
try:
    from typing import Text
except ImportError:
    logger.debug('# Python 3.5.0 and 3.5.1 have incompatible typing modules.', exc_info=True)
    from typing_extensions import Text

# default timeout in seconds for a rest request
DEFAULT_REQUEST_TIMEOUT = 1 * 60


class SnowflakeRestful(object):
    """
        A simple wrapper over python request library to handle retry
    """
    def post(self, url: Text, json: Dict, headers: Dict) -> Dict[Text, Any]:
        """
        Http POST request
        :param url: request url,
        :param json: post request body
        :param headers: request headers, authentication etc
        :return: response payload
        """
        return self._exec_request_with_retry(url=url, method='POST', json=json, headers=headers)

    def get(self, url: Text, headers: Dict) -> Dict[Text, Any]:
        """
        Http GET request
        :param url:
        :param headers:
        :return:
        """
        return self._exec_request_with_retry(url=url, method='GET', headers=headers)

    def _exec_request_with_retry(self, url: Text, method: Text, headers: Dict = None, json: Dict = None) \
            -> Dict[Text, Any]:

        class RetryCtx(object):
            def __init__(self, timeout=None):
                self.retry_count = 0
                self.total_timeout = timeout
                self.next_sleep_time = 1
                self._request_start_time = time.time()

            def sleep_time(self):
                """
                :return: time in seconds to sleep next time, -1 if should not sleep
                """
                if time.time() - self._request_start_time > self.total_timeout:
                    logger.info('Request timeout reached.')
                    return -1
                else:
                    # exponential backoff
                    this_sleep_time = self.next_sleep_time
                    self.next_sleep_time = this_sleep_time * 2
                    self.retry_count += 1
                    logger.info('Retried request. Backoff time %d, Retry count %d',
                                this_sleep_time, self.retry_count)
                    return this_sleep_time

        retry_context = RetryCtx(DEFAULT_REQUEST_TIMEOUT)

        while True:
            try:
                response = self._exec_request(url=url, method=method, headers=headers, json=json)

                if response.ok:
                    return response.json()
                elif self._can_retry(response.status_code):
                    next_sleep_time = retry_context.sleep_time()
                    if next_sleep_time > 0:
                        time.sleep(next_sleep_time)
                        continue

                raise IngestResponseError(response)

            except requests.exceptions.RequestException as e:
                logger.error(f"Request exception occurred: {e}")
                # Handle connection-level errors
                next_sleep_time = retry_context.sleep_time()
                if next_sleep_time > 0:
                    logger.debug(f"Connection error, sleeping for {next_sleep_time} seconds before retry")
                    time.sleep(next_sleep_time)
                    continue
                else:
                    logger.error("Maximum retry timeout reached, giving up")
                    raise e

    def _exec_request(self, url: Text, method: Text, headers: Dict = None, json: Dict = None) -> Response:
        return requests.request(method=method,
                                url=url,
                                headers=headers,
                                json=json)

    @staticmethod
    def _can_retry(http_code):
        return http_code == 408 or 500 <= http_code < 600
