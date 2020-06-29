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

# returns list of all users
def get_users(event, context):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users;")
        result = {}
        result["status"] = 200
        result["body"] = json.dumps(cursor.fetchall(), default=mysql_converter)
        return result

def get_organization_users(event, context):
    org_id = event["org_id"]
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE org_id = %s", (org_id, ))
        result = {}
        result["status"] = 200
        result["body"] = json.dumps(cursor.fetchall(), default=mysql_converter)
        return result

def register_user(event, context):
    result = {}
    try:
        authenticate_api_key(event)
    except Exception as e:
        result["status"] = 401
        result["body"] = repr(e)
        return result

    email = event["email"]
    username = event["username"]
    password = event["password"]
    org_id = event["org_id"]

    try:
        with db.cursor() as cursor:
            sql = "INSERT INTO Users (email, username, password, api_key, org_id, updated_at, created_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW());"
            cursor.execute(sql, (email, username, password, str(uuid4()), org_id))
        db.commit()
    except Exception as e:
        result["status"] = 500
        result["body"] = repr(e)
        return result

    with db.cursor() as cursor:
        sql = "SELECT * FROM Users WHERE email = %s"
        cursor.execute(sql, (email, ))
        result["status"] = 200
        result["body"] = json.dumps(cursor.fetchone(), default=mysql_converter)
        return result
        
def login(event, context):
    username = event["username"]
    password = event["password"]

    with db.cursor() as cursor:
        sql = "SELECT * FROM Users WHERE username = %s and password = %s;"
        cursor.execute(sql, (username, password))
        user = cursor.fetchone()
    
    result = {}
    if user is None:
        result["status"] = 400
        result["body"] = json.dumps({})
        return result

    with db.cursor() as cursor:
        sql = "SELECT * FROM Organizations WHERE id = %s;"
        cursor.execute(sql, (user["org_id"], ))
        user["org"] = cursor.fetchone()

    result["status"] = 200
    result["body"] = json.dumps(user, default=mysql_converter)
    return result


if __name__ == "__main__":
    req = {}
    req["api_key"] = 3
    print(register_user(req, ''))