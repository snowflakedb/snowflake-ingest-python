Snowflake Python Ingest Service SDK 
===================================


.. image:: http://img.shields.io/:license-Apache%202-brightgreen.svg
    :target: http://www.apache.org/licenses/LICENSE-2.0.txt

.. image:: https://travis-ci.org/snowflakedb/snowflake-ingest-python.svg?branch=master
    :target: https://travis-ci.org/snowflakedb/snowflake-ingest-python

.. image:: https://codecov.io/gh/snowflakedb/snowflake-ingest-python/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/snowflakedb/snowflake-ingest-python

.. image:: https://badge.fury.io/py/snowflake-ingest.svg
    :target: https://pypi.python.org/pypi/snowflake-ingest

The Snowflake Ingest Service SDK allows users to ingest files into their Snowflake data warehouse in a programmatic
fashion via key-pair authentication.

Prerequisites
=============

Python 3.4+
-----------
The Snowflake Ingest SDK requires Python 3.4 or above. Backwards compatibility with older versions of Python 3
or any versions of Python 2 is not planned at this time.


A 2048-bit RSA key pair
-----------------------
Snowflake Authentication for the Ingest Service requires creating a 2048 bit
RSA key pair and, registering the public key with Snowflake. For detailed instructions,
please visit the relevant `Snowflake Documentation Page <https://docs.snowflake.com/en/user-guide/authentication.html>`_.


Furl, PyJWT, Requests, and Cryptography
---------------------------------------

Internally, the Snowflake Ingest SDK makes use of `Furl <https://github.com/gruns/furl>`_, 
`PyJWT <https://github.com/jpadilla/pyjwt>`_, and `Requests <https://github.com/psf/requests>`_.
In addition, the `cryptography <https://github.com/pyca/cryptography>`_ is used with PyJWT to sign JWT tokens.


Installation
============ 
If you would like to use this sdk, you can install it using python setuptools.

.. code-block:: bash

    pip install snowflake-ingest
    
Usage
=====
Here is a simple "hello world" example for using ingest sdk.

.. code-block:: python
    
    from logging import getLogger
    from snowflake.ingest import SimpleIngestManager
    from snowflake.ingest import StagedFile
    from snowflake.ingest.utils.uris import DEFAULT_SCHEME
    from datetime import timedelta
    from requests import HTTPError
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.serialization import load_pem_private_key
    from cryptography.hazmat.backends import default_backend
    from cryptography.hazmat.primitives.serialization import Encoding
    from cryptography.hazmat.primitives.serialization import PrivateFormat
    from cryptography.hazmat.primitives.serialization import NoEncryption
    import time
    import datetime
    import os
    import logging

    logging.basicConfig(
            filename='/tmp/ingest.log',
            level=logging.DEBUG)
    logger = getLogger(__name__)


    with open("./rsa_key.p8", 'rb') as pem_in:
      pemlines = pem_in.read()
      private_key_obj = load_pem_private_key(pemlines,
      os.environ['PRIVATE_KEY_PASSPHRASE'].encode(),
      default_backend())

    private_key_text = private_key_obj.private_bytes(
      Encoding.PEM, PrivateFormat.PKCS8, NoEncryption()).decode('utf-8')
    # Assume the public key has been registered in Snowflake:
    # private key in PEM format

    # List of files in the stage specified in the pipe definition
    file_list=['a.csv']
    ingest_manager = SimpleIngestManager(account='testaccount',
                                             host='testaccount.snowflakecomputing.com',
                                             user='ingest_user',
                                             pipe='TESTDB.TESTSCHEMA.TESTPIPE',
                                             private_key=private_key_text)
    # List of files, but wrapped into a class
    staged_file_list = []

    for file_name in file_list:
        staged_file_list.append(StagedFile(file_name, None))

    try:
        resp = ingest_manager.ingest_files(staged_file_list)
    except HTTPError as e:
        # HTTP error, may need to retry
        logger.error(e)
        exit(1)

    # This means Snowflake has received file and will start loading
    assert(resp['responseCode'] == 'SUCCESS')

    # Needs to wait for a while to get result in history
    while True:
        history_resp = ingest_manager.get_history()

        if len(history_resp['files']) > 0:
            print('Ingest Report:\n')
            print(history_resp)
            break
        else:
            # wait for 20 seconds
            time.sleep(20)

        hour = timedelta(hours=1)
        date = datetime.datetime.utcnow() - hour
        history_range_resp = ingest_manager.get_history_range(date.isoformat() + 'Z')

        print('\nHistory scan report: \n')
        print(history_range_resp)
