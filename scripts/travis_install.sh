#!/bin/bash -e
#
# Install Snowflake Ingest Python on travis
#
set -o pipefail

sudo apt-get update
curl -O https://bootstrap.pypa.io/get-pip.py
python get-pip.py
pip --version
pip install -U pytest pytest-cov
pip install .

# white source
echo ${PWD}
chmod 755 ./scripts/run_whitesource.sh
./scripts/run_whitesource.sh
