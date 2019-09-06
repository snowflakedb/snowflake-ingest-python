# Copyright (c) 2012-2017 Snowflake Computing Inc. All rights reserved.

"""
tokentools.py - provides services for automatically creating and renewing
JWT tokens for authenticating to Snowflake
"""

from datetime import timedelta, datetime
from logging import getLogger
from cryptography.exceptions import UnsupportedAlgorithm
from cryptography.hazmat.primitives.serialization import load_pem_private_key
from cryptography.hazmat.primitives.serialization import Encoding
from cryptography.hazmat.primitives.serialization import PublicFormat
from cryptography.hazmat.backends import default_backend
from ..error import IngestClientError
from ..errorcode import ERR_INVALID_PRIVATE_KEY
import base64
import hashlib

import jwt

logger = getLogger(__name__)

try:
    from typing import Text
except ImportError:
    logger.debug('# Python 3.5.0 and 3.5.1 have incompatible typing modules.', exc_info=True)
    from typing_extensions import Text

ISSUER = "iss"
EXPIRE_TIME = "exp"
ISSUE_TIME = "iat"
SUBJECT = "sub"


class SecurityManager(object):
    """
    Given a private key, username, and account, signs and creates tokens for use in Snowflake Ingest Requests
    """
    LIFETIME = timedelta(minutes=59)  # The tokens will have a 59 minute lifetime
    RENEWAL_DELTA = timedelta(minutes=54)  # Tokens will be renewed after 54 minutes
    ALGORITHM = "RS256"  # Tokens will be generated using RSA with SHA256

    def __init__(self, account: Text, user: Text, private_key: Text,
                 lifetime: timedelta = LIFETIME, renewal_delay: timedelta = RENEWAL_DELTA):
        """
        __init__ creates a security manager with the specified context arguments
        :param account: the account in which data is being loaded
        :param user: The user who is loading these files
        :param private_key: the private key we'll use for signing tokens
        :param lifetime: how long this key will live (in minutes)
        :param renewal_delay: how long until the security manager should renew the key
        """

        logger.info(
            """Creating Security Manager with arguments
            account : %s, user : %s, lifetime : %s, renewal_delay : %s""",
            account, user, lifetime, renewal_delay)

        self.account = account.upper()  # Snowflake account names are canonically in all caps
        self.user = user.upper()  # Snowflake user names are also in all caps by default
        self.qualified_username = self.account + "." + self.user  # Generate the full user name
        self.lifetime = lifetime  # the timedelta until our tokens expire
        self.renewal_delay = renewal_delay  # the timedelta until we renew the token
        self.private_key = private_key  # stash the private key
        self.renew_time = datetime.utcnow()  # We need to renew the token NOW
        self.token = None  # We initially have no token

    def get_token(self) -> Text:
        """
        Regenerates the current token if and only if we have exceeded the renewal time
        bounds set
        :return: the new token
        """
        now = datetime.utcnow()  # Fetch the current time

        # If the token has expired, or doesn't exist, regenerate it
        if self.token is None or self.renew_time <= now:
            logger.info("Renewing token because renewal time (%s) is eclipsed by present time (%s)",
                        self.renew_time, now)
            # Calculate the next time we need to renew the token
            self.renew_time = now + self.renewal_delay

            public_key_fp = self.calculate_public_key_fingerprint(self.private_key)

            # Create our payload
            payload = {

                # The issuer is the public key fingerprint
                ISSUER: self.qualified_username + '.' + public_key_fp,

                # subject is user's fully qualified username
                SUBJECT: self.qualified_username,

                # The payload was issued at this point it time
                ISSUE_TIME: now,

                # The token should no longer be accepted after our lifetime has elapsed
                EXPIRE_TIME: now + SecurityManager.LIFETIME
            }

            # Regenerate the actual token
            self.token = jwt.encode(payload, self.private_key, algorithm=SecurityManager.ALGORITHM)
            logger.info("New Token is %s", self.token)

        return self.token.decode('utf-8')

    def calculate_public_key_fingerprint(self, private_key: Text) -> Text:
        """
        Given a private key in pem format, return the public key fingerprint
        :param private_key: private key string
        :return: public key fingerprint
        """
        try:
            private_key = load_pem_private_key(private_key.encode(), None, default_backend())
        except (ValueError,  UnsupportedAlgorithm) as e:
            raise IngestClientError(
                    code=ERR_INVALID_PRIVATE_KEY,
                    message='Invalid private key. {}'.format(e))

        # get the raw bytes of public key
        public_key_raw = private_key.public_key().public_bytes(Encoding.DER, PublicFormat.SubjectPublicKeyInfo)

        # take sha256 on raw bytes and then do base64 encode
        sha256hash = hashlib.sha256()
        sha256hash.update(public_key_raw)

        public_key_fp = 'SHA256:' + base64.b64encode(sha256hash.digest()).decode('utf-8')
        logger.info("Public key fingerprint is %s", public_key_fp)

        return public_key_fp


