#! /usr/bin/env python3

from setuptools import setup

setup(
    name='snowflake_ingest',
    version='0.0.1',
    description='Official SnowflakeDB File Ingest SDK',
    author='Snowflake Computing',
    author_email='support@snowflake.net',
    url='https://www.snowflake.net',
    packages=['snowflake.ingest'],
    license='Apache',
    keywords="snowflake ingest sdk copy loading",
    # From here we describe the package classifiers
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Database"
    ],
    # Now we describe the dependencies
    install_requires=['zodb'],
)
