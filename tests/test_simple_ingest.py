from snowflake.ingest import SimpleIngestManager
from .parameters import CONNECTION_PARAMETERS
from snowflake.ingest import StagedFile
import time
import os
import snowflake.connector
import pytest


def test_simple_ingest(connection_ctx, test_util):
    pipe_name = '{}.{}.TEST_SIMPLE_INGEST_PIPE'.format(
        CONNECTION_PARAMETERS['database'],
        CONNECTION_PARAMETERS['schema'])

    private_key = test_util.read_private_key()

    print(private_key)

    cur = connection_ctx['cnx'].cursor()

    test_file = os.path.join(test_util.get_data_dir(), 'test_file.csv')
    cur.execute('create or replace table TEST_SIMPLE_INGEST_TABLE(c1 number, c2 string)')
    cur.execute('create or replace stage TEST_SIMPLE_INGEST_STAGE')
    cur.execute('put file://{} @TEST_SIMPLE_INGEST_STAGE'.format(test_file))
    cur.execute('create or replace pipe {0} as copy into TEST_SIMPLE_INGEST_TABLE '
                'from @TEST_SIMPLE_INGEST_STAGE'.format(pipe_name))

    ingest_manager = SimpleIngestManager(account=CONNECTION_PARAMETERS['account'],
                                         user=CONNECTION_PARAMETERS['user'],
                                         private_key=private_key,
                                         pipe=pipe_name,
                                         scheme=CONNECTION_PARAMETERS['protocol'],
                                         host=CONNECTION_PARAMETERS['host'],
                                         port=CONNECTION_PARAMETERS['port'])

    staged_files = [StagedFile('test_file.csv.gz', None)]

    resp = ingest_manager.ingest_files(staged_files)

    assert resp['responseCode'] == 'SUCCESS'

    start_polling_time = time.time()

    while time.time() - start_polling_time < 120:
        history_resp = ingest_manager.get_history()

        if len(history_resp['files']) == 1:
            assert history_resp['files'][0]['path'] == 'test_file.csv.gz'
            return
        else:
            # wait for 20 seconds
            time.sleep(20)

    assert False


@pytest.fixture()
def connection_ctx(request):
    cnx = snowflake.connector.connect(**CONNECTION_PARAMETERS)

    def fin():
        cnx.cursor().execute("drop table if exists TEST_SIMPLE_INGEST_TABLE")
        cnx.cursor().execute("drop stage if exists TEST_SIMPLE_INGEST_STAGE")
        cnx.cursor().execute("alter pipe TEST_SIMPLE_INGEST_PIPE set pipe_execution_paused=true")
        cnx.cursor().execute("drop pipe if exists TEST_SIMPLE_INGEST_PIPE")
        cnx.close()
    request.addfinalizer(fin)

    return {'cnx': cnx}
