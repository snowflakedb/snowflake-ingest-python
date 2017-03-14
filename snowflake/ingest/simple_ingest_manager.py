"""
simple_ingest_manager - Creates a basic ingest manager that synchronously sends
requests to the Snowflake Ingest service
"""

# This class will manage our tokens
from .utils import SecurityManager

# This will manage our URL generation
from .utils import URLGenerator
from .utils.uris import DEFAULT_HOST
from .utils.uris import DEFAULT_PORT
from .utils.uris import DEFAULT_SCHEME

# We use a named tuple to represent remote files
from collections import namedtuple

# Typing information
from typing import Text, Dict, Any

# UUID for typing formation
from uuid import UUID

import requests

# We just need a simple named tuple to represent remote files
StagedFile = namedtuple("StagedFile", ["path", "size"])

AUTH_HEADER = "Authorization"  # Authorization header name
BEARER_FORMAT = "BEARER {0}"  # The format of this bearer

OK = 200  # Is this Response OK?


class SimpleIngestManager(object):
    """
    SimpleIngestManager - this class is a simple wrapper around the Snowflake Ingest
    Service rest api. It is *synchronous* and as such we will block until we either totally fail to
    get a response *or* we successfully hear back from the
    """

    def __init__(self, account: Text, user: Text, pipe: Text, private_key: Text,
                 scheme: Text = DEFAULT_SCHEME, host: Text = DEFAULT_HOST, port: int = DEFAULT_PORT):
        """
        Simply instantiates all of our local state
        :param account: the name of the account who is loading
        :param user: the name of the user who is loading
        :param pipe: the name of the pipe which we want to use for ingesting
        :param private_key: the private key we use for token signature
        """
        self.sec_manager = SecurityManager(account, user, private_key)  # Create the token generator
        self.url_engine = URLGenerator(scheme=scheme, host=host, port=port)
        self.pipe = pipe

    def _get_auth_header(self) -> Dict[Text, Text]:
        """
        _get_auth_header - simply method to generate the bearer header for our http requests
        :return: A singleton mapping from bearer to token
        """

        token_bearer = BEARER_FORMAT.format(self.sec_manager.get_token())
        return {AUTH_HEADER: token_bearer}

    def ingest_files(self, staged_files: [StagedFile], request_id: UUID = None) -> Dict[Text, Any]:
        """
        ingest_files - figures out the
        :param staged_files: a list of files we want to ingest
        :param request_id: an optional request uuid to label this request
        :return: the deserialized response from the service
        """
        # Generate the target url
        target_url = self.url_engine.make_ingest_url(self.pipe, request_id)

        # Make our message payload
        payload = {
            "files": [x._asdict() for x in staged_files]
        }

        # Send our request!
        response = requests.post(target_url, json=payload, headers=self._get_auth_header())

        # Now, if we have a response that is not 200, raise an error
        response.raise_for_status()

        # Otherwise, just unpack the message and return that
        return response.json()

    def get_history(self, request_id: UUID = None, recent_seconds: int = None) -> Dict[Text, Any]:
        """
        get_history - returns the currently cached ingest history from the service
        :param request_id: an optional request UUID to label this
        :param recent_seconds: an optional argument that specify the time range that history can be seen
        :return: the deserialized response from the service
        """
        # generate our history endpoint url
        target_url = self.url_engine.make_history_url(self.pipe, request_id, recent_seconds)

        # Send out our request!
        response = requests.get(target_url, headers=self._get_auth_header())

        # If we don't have a valid response, just raise an error
        response.raise_for_status()

        # Otherwise just unpack the message and return that with the status
        return response.json()
