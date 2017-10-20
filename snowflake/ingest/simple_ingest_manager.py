# Copyright (c) 2012-2017 Snowflake Computing Inc. All rights reserved.
"""
simple_ingest_manager - Creates a basic ingest manager that synchronously sends
requests to the Snowflake Ingest service
"""

# This class will manage our tokens
from .utils import SecurityManager

# This will manage our URL generation
from .utils import URLGenerator
from .utils.network import SnowflakeRestful
from .utils.uris import DEFAULT_HOST_FMT
from .utils.uris import DEFAULT_PORT
from .utils.uris import DEFAULT_SCHEME
from .version import __version__

# We use a named tuple to represent remote files
from collections import namedtuple

# Typing information
from typing import Text, Dict, Any

# UUID for typing formation
from uuid import UUID

import sys
import platform

from logging import getLogger
logger = getLogger(__name__)

# We just need a simple named tuple to represent remote files
StagedFile = namedtuple("StagedFile", ["path", "size"])

AUTH_HEADER = "Authorization"  # Authorization header name
BEARER_FORMAT = "BEARER {0}"  # The format of this bearer

USER_AGENT_HEADER = "User-Agent" # User-Agent header name
CLIENT_NAME = u"SnowpipePythonSDK" # Don't change!
CLIENT_VERSION = __version__
PLATFORM = platform.platform()
PYTHON_VERSION = u'.'.join(str(v) for v in sys.version_info[:3])
SNOWPIPE_SDK_USER_AGENT = \
        u'{name}/{version}/{python_version}/{platform}'.format(
                name=CLIENT_NAME,
                version=CLIENT_VERSION,
                python_version=PYTHON_VERSION,
                platform=PLATFORM)

OK = 200  # Is this Response OK?


class SimpleIngestManager(object):
    """
    SimpleIngestManager - this class is a simple wrapper around the Snowflake Ingest
    Service rest api. It is *synchronous* and as such we will block until we either totally fail to
    get a response *or* we successfully hear back from the
    """

    def __init__(self, account: Text, user: Text, pipe: Text, private_key: Text,
                 scheme: Text = DEFAULT_SCHEME, host: Text = None, port: int = DEFAULT_PORT):
        """
        Simply instantiates all of our local state
        :param account: the name of the account who is loading
        :param user: the name of the user who is loading
        :param pipe: the name of the pipe which we want to use for ingesting
        :param private_key: the private key we use for token signature
        """
        self.sec_manager = SecurityManager(account, user, private_key)  # Create the token generator
        self.url_engine = URLGenerator(scheme=scheme,
                                       host=host if host is not None else DEFAULT_HOST_FMT.format(account),
                                       port=port)
        self.pipe = pipe
        self._next_begin_mark = None
        self.restful = SnowflakeRestful()

    def _get_auth_header(self) -> Dict[Text, Text]:
        """
        _get_auth_header - simply method to generate the bearer header for our http requests
        :return: A singleton mapping from bearer to token
        """

        token_bearer = BEARER_FORMAT.format(self.sec_manager.get_token())
        return {AUTH_HEADER: token_bearer}

    def _get_user_agent_header(self) -> Dict[Text, Text]:
        """
        _get_user_agent_header - method to generate the user-agent header for our http requests
        :return: A singleton mapping for user agent and sdk version
        """
        return {USER_AGENT_HEADER: SNOWPIPE_SDK_USER_AGENT}

    def _get_headers(self) -> Dict[Text, Text]:
        """
        _get_headers - get all required SDK headers to be sent to the service
        :return: Array of headers to be sent
        """
        headers = self._get_auth_header()
        headers.update(self._get_user_agent_header())
        return headers

    def ingest_files(self, staged_files: [StagedFile], request_id: UUID = None) -> Dict[Text, Any]:
        """
        ingest_files - Informs Snowflake about the files to be ingested into a table through this pipe
        :param staged_files: a list of files we want to ingest
        :param request_id: an optional request uuid to label this request
        :return: the deserialized response from the service
        """
        # Generate the target url
        target_url = self.url_engine.make_ingest_url(self.pipe, request_id)
        logger.info('Ingest file request url: %s', target_url)

        # Make our message payload
        payload = {
            "files": [x._asdict() for x in staged_files]
        }

        # Send our request!
        headers = self._get_headers()
        response_body = self.restful.post(target_url, json=payload, headers=headers)
        logger.debug('Ingest response: %s', str(response_body))

        return response_body

    def get_history(self, recent_seconds: int = None, request_id: UUID = None) -> Dict[Text, Any]:
        """
        get_history - returns the currently cached ingest history from the service
        :param request_id: an optional request UUID to label this
        :param recent_seconds: an optional argument that specify the time range that history can be seen
        :return: the deserialized response from the service
        """
        # generate our history endpoint url
        target_url = self.url_engine.make_history_url(self.pipe, recent_seconds, self._next_begin_mark, request_id)
        logger.info('Get history request url: %s', target_url)

        # Send out our request!
        headers = self._get_headers()
        response_body = self.restful.get(target_url, headers=headers)

        self._next_begin_mark = response_body['nextBeginMark']
        
        return response_body

    def get_history_range(self, start_time_inclusive: Text, end_time_exclusive: Text = None,
            request_id: UUID = None) -> Dict[Text, Any]:
        """
        get_history_range - returns the ingest history between two points in time
        :param request_id: an optional request UUID to label this
        :param start_time_inclusive: Timestamp in ISO-8601 format. Start of the time range to retrieve load history data.
        :param end_time_exclusive: Timestamp in ISO-8601 format. End of the time range to retrieve load history data.
                                    If omitted, then CURRENT_TIMESTAMP() is used as the end of the range.
        :return: the deserialized response from the service
        """
        # generate our history endpoint url
        target_url = self.url_engine.make_history_range_url(self.pipe, start_time_inclusive, end_time_exclusive, request_id)
        logger.info('Get history range request url: %s', target_url)

        # Send out our request!
        headers = self._get_headers()
        response = self.restful.get(target_url, headers=headers)

        return response

