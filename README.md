# [Assignment Tracker]

**CS178: Cloud and Database Systems — Project #1**
**Author:** [Mikayla Froemming]
**GitHub:** [froemming13]

---

## Overview

This is a web-based grading system that allows a user to manage student records and assignment scores through a simple interface. It allows a user to add, view, update, and delete students while storing their information in a DynamoDB database. The system is designed for teachers or administrators who need a quick way to track students and their performance. It solves the problem of organizing and updating grades by providing a centralized platform.

---

## Technologies Used

- **Flask** — Python web framework
- **AWS EC2** — hosts the running Flask application
- **AWS RDS (MySQL)** — relational database for storing student information, as well as assignment information and grades.
- **AWS DynamoDB** — non-relational database for student information and their grades for assignments.
- **GitHub Actions** — auto-deploys code from GitHub to EC2 on push

---

## Project Structure

```
ProjectOne/
├── flaskapp.py          # Main Flask application — routes and app logic
├── dbCode.py            # Database helper functions (MySQL connection + queries)
├── ProjectOneGrading.sql # SQL database (tables) and corresponding values.
├── creds_sample.py      # Sample credentials file (see Credential Setup below)
├── templates/
│   ├── home.html        # Landing page
│   ├── add_user.html    # Display page for adding a student.
│   ├── delete_user.html # Display page for deleting a student
│   ├── display_user.html # Display page for showing all students on the roster.
│   ├── update_grades.html # Display page to update or add a students grades.
│   ├── low_grades_form.html # Display page to enter grade threshold
│   ├── low_grades.html # Display page to show student grades under the threshold.
├── .gitignore           # Excludes creds.py and other sensitive files
└── README.md
```

---

## How to Run Locally

1. Clone the repository:

   ```bash
   git https://github.com/froemming13/ProjectOne.git
   cd ProjectOne
   ```

2. Install dependencies:

   ```bash
   pip3 install flask pymysql boto3
   ```

3. Set up your credentials (see Credential Setup below)

4. Run the app:

   ```bash
   python3 flaskapp.py
   ```

5. Open your browser and go to `http://127.0.0.1:8080`

---

## How to Access in the Cloud

The app is deployed on an AWS EC2 instance. To view the live version:

```
http://34.202.235.79:8080

```

_(Note: the EC2 instance may not be running after project submission.)_

---

## Credential Setup

This project requires a `creds.py` file that is **not included in this repository** for security reasons.

Create a file called `creds.py` in the project root with the following format (see `creds_sample.py` for reference):

```python
# creds.py — do not commit this file
host = "your-rds-endpoint"
user = "admin"
password = "your-password"
db = "your-database-name"
```

---

## Database Design

### SQL (MySQL on RDS)

The relational database uses three main tables to store students, assignments, and their corresponding grades.

- Students — stores student information such as their name, grade level, and email; primary key is `student_id`
- Assignments — stores assignment details such as title, maximum score, and due date; primary key is `assignment_id`
- Grades — stores the relationship between students and assignments along with their scores; foreign keys link to both tables, `student_id` and `assignment_id`

### The JOIN query used in this project:

#### Grades Below a Certain Percentage:
This is selecting the tables Students, Assignments, and Grades and selecting the given variable we want out of it (i.e. name from Students, title from Assignments). From there we select the main table, Students, and join it together with Grades using the student_id (primary key). We then join Assignments to Grades by using assignment_id (primary key). Finally we use WHERE to select scores from the Grades table that are less than or equal to the provided input from the user.
```mysql
SELECT Students.name, Assignments.title, Grades.score
FROM Students
JOIN Grades ON Students.student_id = Grades.student_id
JOIN Assignments ON Grades.assignment_id = Assignments.assignment_id
WHERE Grades.score <= %s;
```
---
#### Student's Overall Grade:
This is selecting the tables Students, Grades, and Assignments and pulling the variables we need from each respective table (i.e. name from Students, their scores from Grades, and max score from Assignments). From there we join Students and Grades using student_id so we can match students to their scores. We then join Assignments to Grades using the assignment_id so we know how many points each assignment was worth. We group everything by each student and add up their total earned points and total possible points, and then calculate their overall percentage grade from that.
```mysql
SELECT Students.name, SUM(Grades.score) AS earned_points, SUM(Assignments.max_score) AS total_possible, ROUND(SUM(Grades.score) / SUM(Assignments.max_score) * 100, 2) AS average_grade 
FROM Students JOIN Grades ON Students.student_id = Grades.student_id 
JOIN Assignments ON Grades.assignment_id = Assignments.assignment_id 
GROUP BY Students.student_id, Students.name
```
---
### DynamoDB

The DynamoDB table stores student records where each item includes attributes such as their student ID, name, email, and grade level. Each student has a nested list of assignments, and contains assignment ID, title, and score.

- **Table name:** `Students`
- **Partition key:** `student_id`
- **Used for:** storing each student as a single item, including their personal information and a list of their assignments and corresponding scores.

- **Contains:**
- * student_id (partition key) [Number]
- * name [String]
- * email [String]
- * grade_level [Number]
- * assignments [List]
Following items are nested inside the assignments list as maps for each student:
-   * assignment_id [Number]
-   * title [String]
-   * score [Number]

DynamoDB stores related data as one item, allowing the application to quickly retrieve and update a student's assignments without needing queries.

---

## CRUD Operations

| Operation | Route      | Description    |
| --------- | ---------- | -------------- |
| Create    | `/add-student` | Adds a new student to the DynamoDB table with a unique student_id, name, email, grade level, and an empty assignments list.|
| Read      | `/display-students` | Retrieves all students from DynamoDB and displays their information, including assignments and scores in a table format. |
| Update    | `/update-grades` | Updates a student's assignment score. If the assignment does not exist, it creates a new assignment entry with a title and score (used for new students) |
| Delete    | `/delete-student` | Deletes a student from the DynamoDB table based on their student_id. |

---

## Challenges and Insights

The biggest challenge I had was getting MySQL database to properly connect and show up across my local terminal, EC2 instance, and show results on my Flask application. This is partially due to my local device not recognizing `mysql` commands even after multiple rounds of troubleshooting, however it worked through my EC2 instance. I also had a rough time implementing how to append or search through my Assignments table. This is because it is a nested list that holds each assignment and it's information. I did a lot of debugging and work with sections that included the Assignments table (both with CRUD operations AND SQL sections), however I had to turn to ChatGPT to fix a few sections within my CRUD operations to get them to run properly.

In regards to what I learned, I learned more about troubleshooting with my local device and terminal and how to deal with my path files when something is not found or recognized when using my terminal.
<!-- What was the hardest part? What did you learn? Any interesting design decisions? -->

---

## AI Assistance

If sections were not working after a lengthy time of debugging or hassle, I discussed my ideas with ChatGPT and provided current code to improve upon to fix. Each section that used ChatGPT for assistance is marked as such in a comment. Primarily used in sections where I did not know how to use certain functions from documentation, "isinstance" section, minor fixes (importing decimal), and for code primarily used for fixing code associated with the Assignments section. All code provided was refined from previous personal attempts, not entirely written by ChatGPT alone.
