# Copyright (c) 2012-2023 Snowflake Computing Inc. All rights reserved.
"""
test_tokens.py - This defines a series of tests to ascertain that we are
capable of renewing JWT tokens
"""

from snowflake.ingest.utils import SecurityManager
from snowflake.ingest.error import IngestClientError
from snowflake.ingest.errorcode import ERR_INVALID_PRIVATE_KEY
from datetime import timedelta
from time import sleep
import os
import pytest


def test_same_token(test_util):
    """
    Tests that we aren't immediately regenerating the key after each request
    """
    private_key, _ = test_util.generate_key_pair()
    sec_man = SecurityManager("testaccount", "snowman", private_key,
                              renewal_delay=timedelta(seconds=3))
    assert sec_man.get_token() == sec_man.get_token()


def test_regenerate_token(test_util):
    """
    Tests that the security manager generates new tokens after we
    cross the set renewal threshold
    """
    private_key, _ = test_util.generate_key_pair()
    sec_man = SecurityManager("testaccount", "snowman", private_key,
                              renewal_delay=timedelta(seconds=3))
    old_token = sec_man.get_token()
    sleep(5)
    assert old_token != sec_man.get_token()


def test_calculate_public_key_fingerprint(test_util):
    with open(os.path.join(test_util.get_data_dir(), 'test_rsa_key'), 'r') as key_file:
        private_key = key_file.read()
        sec_man = SecurityManager("testaccount", "snowman", private_key,
                                  renewal_delay=timedelta(minutes=3))
        public_key_fingerprint = sec_man.calculate_public_key_fingerprint(private_key)

        assert public_key_fingerprint == 'SHA256:QKX8hnXHVAVXp7mLdCAF+vjU2A8RBuRSpgdRjPHhVWY='


def test_invalid_private_key():
    sec_man = SecurityManager("testaccount", "snowman", 'invalid_private_key',
                              renewal_delay=timedelta(minutes=3))
    with pytest.raises(IngestClientError) as client_error:
        sec_man.get_token()

    assert client_error.value.code == ERR_INVALID_PRIVATE_KEY
