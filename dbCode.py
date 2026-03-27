# dbCode.py
# Author: Mikayla Froemming
# Helper functions for database connection and queries

import pymysql
import creds

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

# boto3 uses the credentials configured via `aws configure` on EC2
dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('Students')
REGION = "us-east-1"
TABLE_NAME = "Students"

def get_conn():
    """Returns a connection to the MySQL RDS instance."""
    conn = pymysql.connect(
        host=creds.host,
        user=creds.user,
        password=creds.password,
        db=creds.db,
    )
    return conn

def get_table():
    """Return a reference to the DynamoDB Students table."""
    dynamodb = boto3.resource("dynamodb", region_name=REGION)
    return dynamodb.Table(TABLE_NAME)

def execute_query(query, args=()):
    """Executes a SELECT query and returns all rows as dictionaries."""
    cur = get_conn().cursor(pymysql.cursors.DictCursor)
    cur.execute(query, args)
    rows = cur.fetchall()
    cur.close()
    return rows

def get_all_students():
    """Scan the Students table and print out each item"""
    table = get_table()
    response = table.scan()
    items = response.get("Items", [])
    students = []
    
    for item in response.get("Items", []):
        student_id = int(item.get("student_id", {}).get("N", 0))
        name = item.get("name", {}).get("S", "Unknown Name")
        email = item.get("email", {}).get("S", "Unknown Email")
        grade_level = int(item.get("grade_level", {}).get("N", 0))

        #consulted with ChatGPT for assistance on this one due to DynamoDB table issues:
        assignments = []
        for a in item.get("assignments", {}).get("L", []):
            am = a.get("M", {})
            assignments.append({
                "assignment_id": int(am.get("assignment_id",{}).get("N", 0)),
                "title": am.get("title", {}).get("S", "Untitled"),
                "score": int(am.get("score", {}).get("N", 0))})

        students.append({
            "student_id": student_id,
            "name": name,
            "email": email,
            "grade_level": grade_level,
            "assignments": assignments
        })
    return students