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
DEFAULT_HOST = "snowflakecomputing.com"  # by default we target the Snowflake US instance
DEFAULT_PORT = 443  # we also target https by default implying 443
DEFAULT_SCHEME = "https"  # we also need to set the scheme to HTTPS

# Our format strings for the endpoints we need target
INGEST_ENDPOINT_FORMAT = "/v1/data/tables/{0}/insertFiles"  # The template for an ingest request endpoint
HISTORY_ENDPOINT_FORMAT = "/v1/data/tables/{0}/insertReport"  # The template for an ingest history endpoint

# Parameter used to pass along request UUIDs
REQUEST_ID_PARAMETER = "requestId"
# Parameter that we use for setting the stage for this url
STAGE_PARAMETER = "stage"


# Method to generate an the URL for an ingest request for a given table, and stage

class URLGenerator(object):
    """
    URLGenerator - this class handles creating the URLs for a requests to
    the Snowflake service
    """
    def __init__(self, scheme: Text = DEFAULT_SCHEME, host: Text = DEFAULT_HOST,  port: int = DEFAULT_PORT):
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

    def make_ingest_url(self, table: Text, stage: Text, uuid: UUID = None) -> Text:
        """
        make_ingest_url - creates a textual representation of the target url we need to hit for
        ingesting files
        :param table: the table into which we want to ingest files (fully qualified)
        :param stage: the stage in which the files live (fully qualified)
        :param uuid: an optional UUID argument to tag this request
        :return: the completed URL
        """

        # Compute the base url
        builder = self._make_base_url(uuid)

        # Set the stage name
        builder.args[STAGE_PARAMETER] = stage

        # Set the path for the ingest url
        builder.path = INGEST_ENDPOINT_FORMAT.format(table)

        return builder.url

    def make_history_url(self, table: Text, uuid: UUID = None) -> Text:
        """
        make_history_url - creates a textual representation of the target url we need to hit for
        history requests
        :param table: the table for which we want to see the see history
        :param uuid: an optional UUID argument to tag this request
        :return: the completed URL
        """

        # Compute the base url
        builder = self._make_base_url(uuid)

        # Set the path for the history url
        builder.path = HISTORY_ENDPOINT_FORMAT.format(table)

        return builder.url
