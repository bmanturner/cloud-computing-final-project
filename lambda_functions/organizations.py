import os
import json
import datetime
from uuid import uuid4
import pymysql
import pymysql.cursors

## GLOBALS

db = pymysql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USERNAME"], passwd=os.environ["DB_PASSWORD"], db=os.environ["DB_NAME"], cursorclass=pymysql.cursors.DictCursor)

## HELPERS

# convert datetime to ISO string
def mysql_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

# read api_key from request and ensure user exists and is an admin
def authenticate_api_key(event):
    if "api_key" not in event:
        raise Exception("An api_key is required to continue")
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE api_key = %s;", (event["api_key"], ))
        user = cursor.fetchone()
        if user is None:
            raise Exception("No user has this api_key")
        if user["role"] != "admin":
            raise Exception("This user is not an admin")
        return user

## FUNCTIONS

# returns list of organizations
def get_organizations(event, context):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Organizations;")
        result = {}
        result["status"] = 200
        result["body"] = json.dumps(cursor.fetchall(), default=mysql_converter)
        return result

def create_organization(event, context):
    result = {}
    try:
        authenticate_api_key(event)
    except Exception as e:
        result["status"] = 401
        result["body"] = repr(e)
        return result

    name = event["name"]
    s3_prefix = event["s3_prefix"].lower()
    result = {}
    if " " in s3_prefix:
        result["status"] = 400
        result["body"] = "s3_prefix can not contain spaces"
        return result

    # create
    try:
        with db.cursor() as cursor:
            sql = "INSERT INTO Organizations (name, s3_prefix) VALUES (%s, %s);"
            cursor.execute(sql, (name, s3_prefix))
        db.commit()
    except Exception as e:
        result["status"] = 500
        result["body"] = repr(e)
        return result

    # return created organization
    with db.cursor() as cursor:
        sql = "SELECT * FROM Organizations WHERE name = %s"
        cursor.execute(sql, (name, ))
        result = {}
        result["status"] = 200
        result["body"] = json.dumps(cursor.fetchone(), default=mysql_converter)
        return result

if __name__ == "__main__":
    req = {}
    req["name"] = "Alpha Dynamics"
    req["s3_prefix"] = "alpha-dynamics"
    req["api_key"] = "651b5ca0-c568-4cb2-9e33-ac9ac4d3d224"
    print(create_organization(req, ''))