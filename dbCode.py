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
    table = get_table() # grabs table
    response = table.scan() # scans table
    items = response.get("Items", []) # gets information from table
    students = [] # empty list to append into
    
    #asked for help regarding isinstance due to decimal.Decimal errors for number entries.
    for item in response.get("Items", []):
        student_id = int(item.get("student_id", 0)) if isinstance(item.get("student_id", 0), decimal.Decimal) else item.get("student_id", 0)
        name = item.get("name", "Unknown Name")
        email = item.get("email", "Unknown Email")
        grade_level = int(item.get("grade_level", 0)) if isinstance(item.get("grade_level", 0), decimal.Decimal) else item.get("grade_level", 0)

        #consulted with ChatGPT for assistance on appending assignments (used decimal.Decimal information from above):
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
        # appending student information collected from prior two code blocks.
        students.append({
            "student_id": student_id,
            "name": name,
            "email": email,
            "grade_level": grade_level,
            "assignments": assignments
        })
    return students

def add_student_to_db(name, email, grade_level):
    """Adds a new student to the DynamoDB table."""
    table = get_table() # grabbing DynamoDB table.

    # used dynamodb documentation for ProjectionExpression to grab only student_id's
    response = table.scan(ProjectionExpression="student_id") # scans table to get all existing student_id's
    items = response.get("Items",[])
    
    # generates a new student_id
    if items:
        student_ids = [int(item["student_id"]) for item in items]
        new_id = max(student_ids) + 1
    else:
        new_id = 10 # starting ID if table is empty or number is taken automatically.

    # creates the student's record
    student = {
        "student_id": new_id,
        "name": name,
        "email": email,
        "grade_level": int(grade_level),
        "assignments": [] # empty list for assignments (if they are added later)
    }

    # inserts student information into DynamoDB
    table.put_item(Item=student)
    return new_id

def delete_student_from_db(student_id):
    """Deletes a student from the DynamoDB table based on student_id."""
    table = get_table()

    # checks if the student exists
    response = table.get_item(Key={"student_id": student_id})

    if "Item" not in response:
        return False # means student was not found
    
    # deletes the student
    table.delete_item(Key={"student_id": student_id})
    return True

def update_student_grades_db(student_id, assignment_id, new_score):
    """Updates or adds a student's assignment and corresponding score."""
    table = get_table()

    # grabs student's record
    response = table.get_item(Key={"student_id": student_id})

    if "Item" not in response:
        return False # means the student was not found

    student = response["Item"]
    assignments = student.get("assignments", []) # grabs any existing assignments

    found = False # if assignment exists
    
    # title map for new assignments (assigns IDs to titles)
    title_map = {
        1: "Homework 1",
        2: "Quiz 1",
        3: "Midterm Exam",
        4: "Homework 2",
        5: "Final Project"
    }

    # looks for existing assignment and updates its score
    # ChatGPT assisted in fixing this code:
    for a in assignments:
        if int(a.get("assignment_id", 0)) == int(assignment_id):
            a["score"] = int(new_score)
            found = True

    # if an assignment is not found, add it in using append
    if not found:
        assignments.append({
            "assignment_id": int(assignment_id),
            "title": title_map.get(int(assignment_id)),
            "score": int(new_score)
        })
    
    # asked ChatGPT for help in this section of code:
    table.update_item(
        Key={"student_id": student_id},
        UpdateExpression="Set assignments = :a",
        ExpressionAttributeValues={":a": assignments}
    )

    return True

def get_low_grades(threshold):
    """Retrieves all student grades below a given threshold using SQL."""
    conn = get_conn() # gets database connection
    cursor = conn.cursor()

    # SQL query to find low grades
    query = """
    SELECT Students.name, Assignments.title, Assignments.max_score, Grades.score
    FROM Students
    JOIN Grades ON Students.student_id = Grades.student_id
    JOIN Assignments on Grades.assignment_id = Assignments.assignment_id
    WHERE (Grades.score / Assignments.max_score)*100 < %s; 
    """
    # executes query with given threshold
    cursor.execute(query, (threshold,))
    results = cursor.fetchall()
    conn.close()

    return results

def get_average_grade():
    """Calculates each student's average grade as a percentage."""
    # SQL query to calculate percentage
    query = """
    SELECT Students.name, SUM(Grades.score) AS earned_points,
    SUM(Assignments.max_score) AS total_possible,
    ROUND(SUM(Grades.score) / SUM(Assignments.max_score) * 100, 2) AS average_grade
    FROM Students
    JOIN Grades ON Students.student_id = Grades.student_id
    JOIN Assignments ON Grades.assignment_id = Assignments.assignment_id
    GROUP BY Students.student_id, Students.name
    """
    # uses execute_query function from above to run the query.
    results = execute_query(query)

    return results