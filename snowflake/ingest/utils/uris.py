# Copyright (c) 2012-2017 Snowflake Computing Inc. All rights reserved.

"""
request_builder.py - Builds the URIs and http requests that we send for ingest
requests and history requests
"""

from uuid import uuid4, UUID
from furl import furl
from typing import Text
from logging import getLogger

# Create a logger for this module
logger = getLogger(__name__)

# URI Construction constants we use for making a target URL
DEFAULT_HOST_FMT = "{}.snowflakecomputing.com"  # by default we target the Snowflake US instance
DEFAULT_PORT = 443  # we also target https by default implying 443
DEFAULT_SCHEME = "https"  # we also need to set the scheme to HTTPS

# Our format strings for the endpoints we need target
INGEST_ENDPOINT_FORMAT = "/v1/data/pipes/{0}/insertFiles"  # The template for an ingest request endpoint
HISTORY_ENDPOINT_FORMAT = "/v1/data/pipes/{0}/insertReport"  # The template for an ingest history endpoint
HISTORY_SCAN_ENDPOINT_FORMAT = "/v1/data/pipes/{0}/loadHistoryScan" # The template for ingest history range endpoint

# Parameter used to pass along request UUIDs
REQUEST_ID_PARAMETER = "requestId"
# Parameter that we use for setting the stage for this url
STAGE_PARAMETER = "stage"
# Parameters for insertReport endpoint
RECENT_HISTORY_IN_SECONDS_PARAMETER = 'recentSeconds'
HISTORY_BEGIN_MARK = 'beginMark'
# Parameters for loadHistoryScan endpoint
HISTORY_RANGE_START_INCLUSIVE = 'startTimeInclusive'
HISTORY_RANGE_END_EXCLUSIVE = 'endTimeExclusive'

# Method to generate an the URL for an ingest request for a given table, and stage
class URLGenerator(object):
    """
    URLGenerator - this class handles creating the URLs for a requests to
    the Snowflake service
    """
    def __init__(self, host: Text, scheme: Text = DEFAULT_SCHEME, port: int = DEFAULT_PORT):
        """
        This constructor simply stashes the basic portions of the request URL such that the user
        doesn't have to repeatedly provide them
        """
        self.scheme = scheme
        self.host = host
        self.port = port

    def _make_base_url(self, uuid: UUID = None) -> furl:
        """
        _makeBaseURL - generates the common base URL for all of our requests
        :param uuid: a UUID we want to attach to the
        :return: the furl wrapper around our unfinished base url
        """
        base = furl()  # Create an uninitialized base URI object
        base.host = self.host  # set the host name
        base.port = self.port  # set the port number
        base.scheme = self.scheme  # set the access scheme

        # if we have no uuid to attach to this request, generate one
        if uuid is None:
            uuid = uuid4()

        # Set the request id parameter uuid
        base.args[REQUEST_ID_PARAMETER] = str(uuid)

        return base

    def make_ingest_url(self, pipe: Text, uuid: UUID = None) -> Text:
        """
        make_ingest_url - creates a textual representation of the target url we need to hit for
        ingesting files
        :param pipe: the pipe which we want to use to ingest files (fully qualified)
        :param uuid: an optional UUID argument to tag this request
        :return: the completed URL
        """

        # Compute the base url
        builder = self._make_base_url(uuid)

        # Set the path for the ingest url
        builder.path = INGEST_ENDPOINT_FORMAT.format(pipe)

        return builder.url

    def make_history_url(self, pipe: Text, recent_seconds: int = None,
            begin_mark: Text = None, uuid: UUID = None) -> Text:
        """
        make_history_url - creates a textual representation of the target url we need to hit for
        history requests
        :param pipe: the pipe for which we want to see the see history
        :param uuid: an optional UUID argument to tag this request
        :param recent_seconds: an optional argument to specify recent seconds
        :param begin_mark: an optional argument used to indicate from which record should next reponse
                           return
        :return: the completed URL
        """

        # Compute the base url
        builder = self._make_base_url(uuid)

        # Set the path for the history url
        builder.path = HISTORY_ENDPOINT_FORMAT.format(pipe)
        
        if recent_seconds is not None:
            builder.args[RECENT_HISTORY_IN_SECONDS_PARAMETER] = str(recent_seconds)

        if begin_mark is not None:
            builder.args[HISTORY_BEGIN_MARK] = str(begin_mark)

        return builder.url

    def make_history_range_url(self, pipe: Text, start_time_inclusive: Text,
            end_time_exclusive: Text = None, uuid: UUID = None) -> Text:
        """
        make_history_url - creates [M#Ka textual representation of the target url we need to hit for
        history range scan requests
        :param pipe: the pipe for which we want to see the see history
        :param uuid: an optional UUID argument to tag this request
        :param start_time_inclusive: Timestamp in ISO-8601 format. Start of the time range to retrieve load history data.
        :param end_time_exclusive: Timestamp in ISO-8601 format. End of the time range to retrieve load history data.
                                    If omitted, then CURRENT_TIMESTAMP() is used as the end of the range.
        :return: the completed URL
        """

        # Compute the base url
        builder = self._make_base_url(uuid)

        # Set the path for the history url
        builder.path = HISTORY_SCAN_ENDPOINT_FORMAT.format(pipe)

        builder.args[HISTORY_RANGE_START_INCLUSIVE] = start_time_inclusive

        if end_time_exclusive is not None:
            builder.args[HISTORY_RANGE_END_EXCLUSIVE] = end_time_exclusive

        return builder.url
