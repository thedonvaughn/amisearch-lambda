#!/usr/bin/env bash

# Exit immediately if a command exits with a non-zero status.
set -e

if [ -z "$1" ] ; then echo "Please provide path to s3 bucket and key (e.g. s3://mybucket/lambda/foo.zip)"; exit 1; fi

TMP=$(mktemp -d)
echo "Created temp dir: ${TMP}"
cp function/*.py ${TMP}/
pip install requests -t ${TMP}
cd "${TMP}"
zip -r amisearch.zip .
aws s3 cp amisearch.zip "$1"
rm -rf "${TMP}"
