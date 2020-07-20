#!/bin/bash
set -e
ARTIFACT_BUCKET=lambda-artifacts-sharebox
aws cloudformation package --template-file template.yml --s3-bucket $ARTIFACT_BUCKET --output-template-file out.yml
aws cloudformation deploy --template-file out.yml --stack-name sharebox --capabilities CAPABILITY_NAMED_IAM