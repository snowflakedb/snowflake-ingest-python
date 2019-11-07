#  Copyright (c) 2012-2017 Snowflake Computing Inc. All rights reserved.
import pytest
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import snowflake.connector
import uuid
from .parameters import CONNECTION_PARAMETERS
from .parameters import PRIVATE_KEY_1_PASSPHRASE
from snowflake.connector.compat import TO_UNICODE


if os.getenv('TRAVIS') == 'true':
    TEST_SCHEMA = 'TRAVIS_JOB_{0}'.format(os.getenv('TRAVIS_JOB_ID'))
else:
    TEST_SCHEMA = 'python_connector_tests_' + TO_UNICODE(uuid.uuid4()).replace(
        '-', '_')


class TestUtil:

    @staticmethod
    def get_data_dir():
        tests_dir = os.path.dirname(os.path.realpath(__file__))
        return os.path.join(tests_dir, "data")

    @staticmethod
    def generate_key_pair():
        private_key = rsa.generate_private_key(backend=default_backend(),
                                               public_exponent=65537,
                                               key_size=2048)

        private_key_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        ).decode('utf-8')

        public_key_in_pem = private_key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo).decode('utf-8')

        return private_key_pem, public_key_in_pem

    @staticmethod
    def read_private_key():
        """
        Add your own rsa private key(for testing only) in tests directory
        Follow instructions here
        https://docs.snowflake.net/manuals/user-guide/data-load-snowpipe-rest-gs.html#using-key-pair-authentication
        :return: private key pem encoded
        """
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


@pytest.fixture(scope='session', autouse=True)
def init_test_schema(request):
    """
    Initializes and Deinitializes the test schema
    This is automatically called per test session.
    """
    param = get_cnx_param()
    with snowflake.connector.connect(**param) as con:
        # Uncomment below two lines to test it locally, travis user account
        # doesnt have permissions to create db and schema
        # con.cursor().execute("CREATE OR REPLACE DATABASE {0}".format(TEST_DB))
        # con.cursor().execute("USE DATABASE {0}".format(TEST_DB))
        con.cursor().execute(
            "CREATE SCHEMA IF NOT EXISTS {0}".format(TEST_SCHEMA))
        # con.cursor().execute("USE SCHEMA {0}".format(TEST_SCHEMA))

    def fin():
        param1 = get_cnx_param()
        with snowflake.connector.connect(**param1) as con1:
            con1.cursor().execute(
                "DROP SCHEMA IF EXISTS {0}".format(TEST_SCHEMA))
    request.addfinalizer(fin)


@pytest.fixture()
def test_util():
    return TestUtil


@pytest.fixture()
def connection_ctx(request):
    param = get_cnx_param()
    cnx = snowflake.connector.connect(**param)

    def fin():
        cnx.close()
    request.addfinalizer(fin)

    return {'cnx': cnx, 'param': param}


def get_cnx_param():
    param = CONNECTION_PARAMETERS
    param['schema'] = TEST_SCHEMA
    return param
