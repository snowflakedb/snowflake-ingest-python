#! /usr/bin/env python3

# We need this to define our package
from setuptools import setup

# We use this to find and deploy our unittests
import unittest
import os
# We need to know the version to backfill some dependencies
from sys import version_info, exit
# Define our list of installation dependencies
DEPENDS = ["pyjwt", "snowflake-connector-python", "furl", "cryptography"]

# If we're at version less than 3.4 - fail
if version_info[0] < 3 or version_info[1] < 4:
    exit("Unsupported version of Python. Minimum version for the Ingest SDK is 3.4")

# If we're at version 3.4, backfill the typing library
elif version_info[1] == 4:
    DEPENDS.append("typing")

here = os.path.abspath(os.path.dirname(__file__))

def test_suite():
    """
    Defines the test suite for the snowflake ingest SDK
    """
    loader = unittest.TestLoader()
    return loader.discover("tests", pattern="test_*.py")

about = {}
with open(os.path.join(here, 'snowflake', 'ingest', 'version.py'),
          mode='r', encoding='utf-8') as f:
    exec(f.read(), about)

__version__ = about['__version__']

if 'SF_BUILD_NUMBER' in os.environ:
    __version__ += ('.' + str(os.environ['SF_BUILD_NUMBER']))

with open(os.path.join(here, 'DESCRIPTION.rst'), encoding='utf-8') as f:
        long_description = f.read()

setup(
    name='snowflake_ingest',
    version=__version__,
    description='Official SnowflakeDB File Ingest SDK',
    long_description=long_description,
    author='Snowflake Computing',
    author_email='support@snowflake.net',
    url='https://www.snowflake.net',
    packages=['snowflake.ingest',
              'snowflake.ingest.utils'],
    license='Apache',
    keywords="snowflake ingest sdk copy loading",

    package_data={
        'snowflake.ingest':['*.rst', 'LICENSE']
    },
    # From here we describe the package classifiers
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Topic :: Database"
    ],
    # Now we describe the dependencies
    install_requires=DEPENDS,
    # At last we set the test suite
    test_suite="setup.test_suite"
)
