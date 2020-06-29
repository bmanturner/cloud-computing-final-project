import os
import json
import datetime
from uuid import uuid4
import pymysql
import pymysql.cursors

## GLOBALS

db = pymysql.connect(host=os.environ["DB_HOST"], user=os.environ["DB_USERNAME"], passwd=os.environ["DB_PASSWORD"], db=os.environ["DB_NAME"], cursorclass=pymysql.cursors.DictCursor)

## HELPERS

def mysql_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()

## FUNCTIONS

def get_organizations(event, context):
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM Organizations;")
        result = {}
        result["status"] = 200
        result["body"] = json.dumps(cursor.fetchall(), default=mysql_converter)
        return result

def create_organization(event, context):
    name = event["name"]
    s3_prefix = event["s3_prefix"].lower()
    result = {}
    if " " in s3_prefix:
        result["status"] = 400
        result["body"] = "s3_prefix can not contain spaces"
        return result

    with db.cursor() as cursor:
        sql = "INSERT INTO Organizations (name, s3_prefix) VALUES (%s, %s);"
        cursor.execute(sql, (name, s3_prefix))
    db.commit()

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
    print(create_organization(req, ''))