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


Furl, PyJWT, Requests
---------------------

Internally, the Snowflake Ingest SDK makes use of `Furl <https://github.com/gruns/furl>`_, 
`PyJWT <https://github.com/jpadilla/pyjwt>`_, and `Requests <http://docs.python-requests.org/en/master/>`_.


Installation
============
If you would like to use this sdk, you can install it using python setuptools.

.. code-block:: bash

    pip install snowflake-ingest