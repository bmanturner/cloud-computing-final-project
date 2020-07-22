#!/bin/bash
STACK=sharebox
aws cloudformation delete-stack --stack-name $STACK
echo "Deleted $STACK stack."
