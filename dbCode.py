# dbCode.py
# Author: Mikayla Froemming
# Helper functions for database connection and queries

import pymysql
import creds

import boto3
from boto3.dynamodb.conditions import Key
from boto3.dynamodb.conditions import Attr

import decimal #fixing errors in viewing all students.

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
    
    #asked for help regarding isinstance due to decimal.Decimal errors for number entries.
    for item in response.get("Items", []):
        student_id = int(item.get("student_id", 0)) if isinstance(item.get("student_id", 0), decimal.Decimal) else item.get("student_id", 0)
        name = item.get("name", "Unknown Name")
        email = item.get("email", "Unknown Email")
        grade_level = int(item.get("grade_level", 0)) if isinstance(item.get("grade_level", 0), decimal.Decimal) else item.get("grade_level", 0)

        #consulted with ChatGPT for assistance on appending assignments (used decimal.Decimal information from above)::
        assignments = []
        for a in item.get("assignments", []):
            assignment_id = int(a.get("assignment_id", 0)) if isinstance(a.get("assignment_id", 0), decimal.Decimal) else a.get("assignment_id", 0)
            title = a.get("title", "Untitled")
            score = int(a.get("score", 0)) if isinstance(a.get("score", 0), decimal.Decimal) else a.get("score", 0)
            assignments.append({
                "assignment_id": assignment_id,
                "title": title,
                "score": score
            })

        students.append({
            "student_id": student_id,
            "name": name,
            "email": email,
            "grade_level": grade_level,
            "assignments": assignments
        })
    return students

def add_student_to_db(name, email, grade_level):
    table = get_table()

    # used dynamodb documentation for ProjectionExpression
    response = table.scan(ProjectionExpression="student_id")
    items = response.get("Items",[])
    
    if items:
        student_ids = [int(item["student_id"]) for item in items]
        new_id = max(student_ids) + 1
    else:
        new_id = 10

    #student record
    student = {
        "student_id": new_id,
        "name": name,
        "email": email,
        "grade_level": int(grade_level),
        "assignments": []
    }

    table.put_item(Item=student)
    return new_id

def delete_student_from_db(student_id):
    table = get_table()

    response = table.get_item(Key={"student_id": student_id})

    if "Item" not in response:
        return False
    
    table.delete_item(Key={"student_id": student_id})
    return True

def update_student_grades_db(student_id, assignment_id, new_score):
    table = get_table()

    response = table.get_item(Key={"student_id": student_id})

    if "Item" not in response:
        return False
    found = False

    student = response["Item"]
    assignments = student.get("assignments", [])

    for a in assignments:
        if int(a.get("assignment_id", 0)) == int(assignment_id):
            a["score"] = int(new_score)
            found = True

    if not found:
        return False
    
    #asked chatgpt for help in this section:
    table.update_item(
        Key={"student_id": student_id},
        UpdateExpression="Set assignments = :a",
        ExpressionAttributeValues={":a": assignments}
    )

    return True
