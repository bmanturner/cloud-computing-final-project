import os
import json
import datetime
from uuid import uuid4
import pymysql
import pymysql.cursors

## GLOBALS

# connection to database (mysql)
db = pymysql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USERNAME"], passwd=os.environ["DB_PASSWORD"], db=os.environ["DB_NAME"], cursorclass=pymysql.cursors.DictCursor)

## HELPERS

# convert datetime to ISO string so we can return python dicts as JSON
def mysql_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

# read api_key from request and ensure user exists and is an admin or an org_admin
def authenticate_api_key(event):
    if "api_key" not in event:
        raise Exception("An api_key is required to continue")
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE api_key = %s;", (event["api_key"], ))
        user = cursor.fetchone()
        if user is None:
            raise Exception("No user has this api_key")
        if user["role"] not in ["admin", "org_admin"]:
            raise Exception("This user is not an admin")
        return user

## UNAUTHENTICATED FUNCTIONS

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

# AUTHENTICATED FUNCTIONS (api_key required)

# admin can create users in any organization
# org_admin can only create users in their own organization
def register_user(event, context):
    result = {}
    try:
        calling_user = authenticate_api_key(event)
    except Exception as e:
        result["status"] = 401
        result["body"] = repr(e)
        return result

    email = event["email"]
    username = event["username"]
    password = event["password"]
    role = event["role"]
    org_id = event["org_id"]
    # check valid role
    if role not in ["admin", "org_admin", "client"]:
        result["status"] = 400
        result["body"] = "Possible roles are admin, org_admin, and client"
        return result
    # enforce user creation rules
    if calling_user["role"] == "org_admin" and calling_user["org_id"] != org_id:
        result["status"] = 401
        result["body"] = "You are not permitted to create users in another organization"
        return result

    try:
        with db.cursor() as cursor:
            sql = "INSERT INTO Users (email, username, password, api_key, org_id, updated_at, created_at, role) VALUES (%s, %s, %s, %s, %s, NOW(), NOW(), %s);"
            cursor.execute(sql, (email.strip(), username.strip(), password.strip(), str(uuid4()), org_id, role.strip()))
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

# admin can edit any user role
# org_admin can only edit user role in their organization
def edit_user_role(event, context):
    result = {}
    try:
        calling_user = authenticate_api_key(event)
    except Exception as e:
        result["status"] = 401
        result["body"] = repr(e)
        return result
    
    user_id = event["user_id"]
    new_role = event["role"]
    if new_role not in ["admin", "org_admin", "client"]:
        result["status"] = 400
        result["body"] = "Possible roles are admin, org_admin, and client"
        return result

    # check org of user to update to enforce update role rules
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Users WHERE id = %s", (user_id, ))
        user = cursor.fetchone()
        if user is None:
            result["status"] = 404
            result["body"] = "A user with that user_id does not exist"
            return result
    if calling_user["role"] == "org_admin" and calling_user["org_id"] != user["org_id"]:
        result["status"] = 401
        result["body"] = "An org_admin user can only modify users in their own organization"
        return result
    
    # update user role
    try: 
        with db.cursor() as cursor:
            cursor.execute("UPDATE Users SET role = %s WHERE id = %s", (new_role, user_id))
        db.commit()
    except Exception as e:
        result["status"] = 500
        result["body"] = repr(e)

    result["status"] = 200
    result["body"] = "Successfully updated user role"
    return result

if __name__ == "__main__":
    print(get_users('', ''))


    req = {}
    req["role"] = "client"
    req["api_key"] = "2b0e6a26-4b4a-4461-96b7-9085de4cc344"
    req["user_id"] = 79
    # print(edit_user_role(req, ''))