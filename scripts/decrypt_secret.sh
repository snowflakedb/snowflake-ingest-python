#!/bin/sh

# Decrypt the file
# --batch to prevent interactive command --yes to assume "yes" for questions

gpg --quiet --batch --yes --decrypt --passphrase="$DECRYPTION_PASSPHRASE" \
  --output ./tests/parameters.py ./tests/parameters.py.gpg