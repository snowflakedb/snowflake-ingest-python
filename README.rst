Snowflake Python Ingest Service SDK 
===================================


.. image:: http://img.shields.io/:license-Apache%202-brightgreen.svg
    :target: http://www.apache.org/licenses/LICENSE-2.0.txt

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
please visit the relevant `Snowflake Documentation Page <docs.snowflake.net>`_.


Furl, PyJWT, Requests, and Cryptography
---------------------------------------

Internally, the Snowflake Ingest SDK makes use of `Furl <https://github.com/gruns/furl>`_, 
`PyJWT <https://github.com/jpadilla/pyjwt>`_, and `Requests <http://docs.python-requests.org/en/master/>`_.
In addition, the `cryptography <https://cryptography.io/en/latest/>`_ is used with PyJWT to sign JWT tokens.


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
    import time
    from requests import HTTPError
    
    logger = getLogger(__name__) 

    # assume public key has been registered in Snowflake 
    # private key in pem format
    private_key="""
    -----BEGIN PRIVATE KEY-----
    abc...
    -----END PRIVATE KEY-----"""
    
    # file lists that already in the stage that specified in pipe definition
    file_list=['a.csv', 'b.csv']
    ingest_manager = SimpleIngestManager(account='testaccount',
                                         user='ingest_user',
                                         pipe='TESTDB.TESTSCHEMA.TESTPIPE',
                                         private_key=private_key)
    # list of files, but wrapped into a class  
    staged_file_list = []                               
    for file_name in file_list:
        staged_file_list.append(StagedFile(file_name, None))

    try: 
        resp = ingest_manager.ingest_files(staged_file_list)
    except IngestResponseError as e:
        logger.error(e)
        exit(1)

    # This means Snowflake has received file and will start loading
    assert(resp['responseCode'] == 'SUCCESS')   

    # Needs to wait for a while to get result in history
    while True:
        history_resp = ingest_manager.get_history()

        if len(history_resp['files']) == 2:
            print('Ingest Report:\n')
            print(history_resp)
            break
        else:
            # wait for 20 seconds
            time.sleep(20)

    // Valid ISO 8601 format requires Z at the end
    hour = timedelta(hours=1)
    date = datetime.datetime.utcnow() - hour
    history_range_resp = ingest_manager.get_history_range(date.isoformat() + 'Z')

    print('\nHistory scan report: \n')
    print(history_range_resp)
