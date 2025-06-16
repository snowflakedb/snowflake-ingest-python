This package includes the Snowpipe python SDK

Snowflake Documentation is available at:
https://docs.snowflake.net/

Source code is also available at: https://github.com/snowflakedb/snowflake-ingest-python

Release Notes
-------------------------------------------------------------------------------
- v1.0.11 (June 17, 2025)

      - Better handling to retry connection errors
      - Pin dependency package to newer version (snowflake-connector-python)

- v1.0.10 (November 14, 2024)

      - Update readme for artifact validation using cosign

- v1.0.9 (September 10, 2024)

      - Fix casing for RFC-6750 conformity
      - Handle unexpected json structure in error payload

- v1.0.8 (July 03, 2024)
      - Update dependency package to newer version (requests)

- v1.0.7 (January 05, 2024)

      - Pin dependency package to newer version (snowflake-connector-python)

- v1.0.6 (November 08, 2023)

      - Pin dependency package to newer version (requests)

- v1.0.5 (November 04, 2022)

      - Pin dependency package to newer versions (requests, snowflake-connector-python)
      - Fix pyJwt logic to allow for version >= 2.0.0
      
- v1.0.4 (May 11, 2021)

      - Support a special account name style.

- v1.0.3 (January 11, 2021)

      - Use older version of pyJwt by pinning the version(<2.0.0)

- v1.0.2 (March 09, 2020)

      - Stop logging JWT token

- v1.0.1 (November 08, 2019)

      - Replaced Botocore's vendored requests with standalone requests

- v1.0.0 (September 19, 2018)

      - Fix typing package issue in python 3.5.0 and 3.5.1
      - Support key rotation in key pair authentication

- v0.9.1 (November 9, 2017)

      - Public preview release
