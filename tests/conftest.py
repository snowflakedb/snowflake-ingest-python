#  Copyright (c) 2012-2017 Snowflake Computing Inc. All rights reserved.
import pytest
import os
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
import snowflake.connector
import random

from .parameters import CONNECTION_PARAMETERS
import logging
logging.basicConfig(
    filename='/tmp/test_ingest.log',
    level=logging.DEBUG)

logger = logging.getLogger(__name__)

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
    def clear_ingest_ctx(ctx_id, cnx):
        cur = cnx.cursor()
        test_user = 'test_user_{}'.format(ctx_id)
        test_role = 'test_role_{}'.format(ctx_id)
        test_stage = 'test_stage_{}'.format(ctx_id)
        test_table = 'snowpipe_smoke_test_py'
        test_pipe = 'test_pipe_{}'.format(ctx_id)

        cur.execute('use role {}'.format(test_role))
        cur.execute('drop pipe {}'.format(test_pipe))

        cur.execute('use role testrole_snowpipe_python')
        cur.execute('drop stage if exists {}'.format(test_stage))
        cur.execute('truncate table {}'.format(test_table))

        cur.execute('use role accountadmin')
        cur.execute('drop role {}'.format(test_role))
        cur.execute('drop user {}'.format(test_user))


@pytest.fixture()
def test_util():
    return TestUtil


@pytest.fixture()
def ingest_ctx(request):
    cnx = snowflake.connector.connect(**CONNECTION_PARAMETERS)

    ctx_id = ''.join(random.choice('0123456789ABCDEF') for i in range(8))
    test_user = 'test_user_{}'.format(ctx_id)
    test_role = 'test_role_{}'.format(ctx_id)
    test_stage = 'test_stage_{}'.format(ctx_id)
    #test_table = 'test_table_{}'.format(ctx_id)
    # for now hard code the value for smoke test purpose,
    # revisit this when we need to add more tests
    test_table = 'snowpipe_smoke_test_py'
    test_pipe = 'test_pipe_{}'.format(ctx_id)

    private_key, public_key = TestUtil.generate_key_pair()

    # strip off header in public key pem
    public_key = ''.join(public_key.split('\n')[1:-2])

    cur = cnx.cursor()

    # create ingest object
    cur.execute('use role accountadmin')
    cur.execute('create or replace role {}'.format(test_role))
    cur.execute('create or replace user {} default_role={}'
                .format(test_user, test_role))
    cur.execute('alter user {} set rsa_public_key=\'{}\''.format(
        test_user, public_key))
    cur.execute('grant role {} to user {}'.format(test_role, test_user))
    cur.execute('grant role {} to user TEST_SNOWPIPE_PYTHON'.format(test_role))

    cur.execute('use role testrole_snowpipe_python')
    cur.execute('create or replace stage {}'.format(test_stage))
    cur.execute('create table if not exists {}(cola number, colb string)'
                .format(test_table))
    cur.execute('create or replace pipe {} as copy into {} from @{}'
                .format(test_pipe, test_table, test_stage))

    # grant privilege
    cur.execute('grant usage on database TESTDB_SNOWPIPE_PYTHON to role {}'
                .format(test_role))
    cur.execute('grant usage on schema TESTSCHEMA_SNOWPIPE_PYTHON to role {}'
                .format(test_role))
    cur.execute('grant read on stage {} to role {}'
                .format(test_stage, test_role))
    cur.execute('grant ownership on pipe {} to role {}'
                .format(test_pipe, test_role))
    cur.execute('grant select, insert on table {} to role {}'
                .format(test_table, test_role))

    def fin():
        TestUtil.clear_ingest_ctx(ctx_id, cnx)
        cnx.close()
    request.addfinalizer(fin)

    return {'id': ctx_id, 'private_key': private_key, 'cnx': cnx}
