# cloud-computing-final-project
CS 403/633/733 Final Project - Dropbox Clone

## Lambda Function Development

### Getting Set-up

1. Install [AWS cli](https://docs.aws.amazon.com/cli/index.html)
2. Install python3 (v3.8+)
3. `cd lambda_functions`
4. `pip install -r requirements.txt`
5. Run functions using example code in `__main__` (in each file)
6. Create new functions?

### Need to know

* If you run users.py you can get a list of existing users
* Authorized functions require an api_key to call (every user has one)
* Only users with admin or org_admin role can call certain functions
* An admin can do anything, an org_admin can do things that affect their organization
* Each function must take an `event` and `context` argument
* The `event` argument is a dict that contains request information (REST arguments)
* Do not attempt to create a module of shared code without first researching 'aws lambda layers with cloudformation'

## Python Client

### Disclaimer

This project is meant to demonstrate skills learned in a cloud computing course and is not production ready. 