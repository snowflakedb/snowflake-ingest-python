from snowflake.ingest import SimpleIngestManager
from .parameters import CONNECTION_PARAMETERS
from snowflake.ingest import StagedFile
import time
import os


def test_simple_ingest(ingest_ctx, test_util):
    ingest_user = 'TEST_USER_{}'.format(ingest_ctx['id'])
    private_key = ingest_ctx['private_key']
    pipe_name = '{}.{}.TEST_PIPE_{}'.format(CONNECTION_PARAMETERS['database'],
                                            CONNECTION_PARAMETERS['schema'],
                                            ingest_ctx['id'])

    ingest_manager = SimpleIngestManager(account=CONNECTION_PARAMETERS['account'],
                                         user=ingest_user,
                                         private_key=private_key,
                                         pipe=pipe_name,
                                         scheme=CONNECTION_PARAMETERS['protocol'],
                                         host=CONNECTION_PARAMETERS['host'],
                                         port=CONNECTION_PARAMETERS['port'])

    test_file = os.path.join(test_util.get_data_dir(), 'test_file.csv')
    ingest_ctx['cnx'].cursor().execute('put file://{} @TEST_STAGE_{}'.format(test_file, ingest_ctx['id']))

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

