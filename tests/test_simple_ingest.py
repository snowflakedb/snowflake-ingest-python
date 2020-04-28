from snowflake.ingest import SimpleIngestManager
from snowflake.ingest import StagedFile
import time
import os


def test_simple_ingest(connection_ctx, test_util):
    param = connection_ctx['param']

    pipe_name = '{}.{}.TEST_SIMPLE_INGEST_PIPE'.format(
        param['database'],
        param['schema'])

    private_key = test_util.read_private_key()

    cur = connection_ctx['cnx'].cursor()

    test_file = os.path.join(test_util.get_data_dir(), 'test_file.csv')
    cur.execute('create or replace table TEST_SIMPLE_INGEST_TABLE(c1 number, c2 string)')
    cur.execute('create or replace stage TEST_SIMPLE_INGEST_STAGE')
    cur.execute('put file://{} @TEST_SIMPLE_INGEST_STAGE'.format(test_file))
    cur.execute('create or replace pipe {0} as copy into TEST_SIMPLE_INGEST_TABLE '
                'from @TEST_SIMPLE_INGEST_STAGE'.format(pipe_name))

    ingest_manager = SimpleIngestManager(account=param['account'],
                                         user=param['user'],
                                         private_key=private_key,
                                         pipe=pipe_name,
                                         scheme=param['protocol'],
                                         host=param['host'],
                                         port=param['port'])

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

