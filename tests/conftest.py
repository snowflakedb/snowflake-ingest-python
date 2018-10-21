#  Copyright (c) 2012-2017 Snowflake Computing Inc. All rights reserved.
import pytest
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from .parameters import CONNECTION_PARAMETERS
from .parameters import PRIVATE_KEY_1_PASSPHRASE


class TestUtil:

    @staticmethod
    def get_data_dir():
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(tests_dir, "data")

    @staticmethod
    def read_private_key():
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        private_key_filename = os.path.join(tests_dir, "sfctest0_private_key_1.p8")

        with open(private_key_filename, "rb") as private_key_file:
            private_key = serialization.load_pem_private_key(
                private_key_file.read(),
                password=PRIVATE_KEY_1_PASSPHRASE.encode('utf-8'),
                backend=default_backend()
            )

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()).decode('utf-8')

        return private_key_pem


@pytest.fixture()
def test_util():
    return TestUtil


