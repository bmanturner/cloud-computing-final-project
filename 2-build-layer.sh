#!/bin/bash
set -e
rm -rf package
cd lambda_functions
pip3 install --target ../package/python -r requirements.txt