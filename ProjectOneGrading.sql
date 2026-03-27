-- Create and use database
CREATE DATABASE IF NOT EXISTS grading;
USE grading;

-- Drop tables if they already exist (prevents errors if you rerun)
DROP TABLE IF EXISTS Grades;
DROP TABLE IF EXISTS Students;
DROP TABLE IF EXISTS Assignments;

-- Students table
CREATE TABLE Students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    grade_level INT,
    email VARCHAR(100)
);

-- Assignments table
CREATE TABLE Assignments (
    assignment_id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(100) NOT NULL,
    max_score INT NOT NULL,
    due_date DATE
);

-- Grades table (must come after the other two)
CREATE TABLE Grades (
    grade_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT,
    assignment_id INT,
    score INT,
    FOREIGN KEY (student_id) REFERENCES Students(student_id) ON DELETE CASCADE,
    FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id) ON DELETE CASCADE
);

-- Insert Students
INSERT INTO Students (name, grade_level, email) VALUES
('Alice Johnson', 10, 'alice@example.com'),
('Brian Smith', 11, 'brian@example.com'),
('Cathy Lee', 10, 'cathy@example.com'),
('David Brown', 12, 'david@example.com');

-- Insert Assignments
INSERT INTO Assignments (title, max_score, due_date) VALUES
('Homework 1', 100, '2026-03-01'),
('Quiz 1', 50, '2026-03-05'),
('Midterm Exam', 100, '2026-03-15'),
('Homework 2', 100, '2026-03-20'),
('Final Project', 150, '2026-04-10');

-- Insert Grades
INSERT INTO Grades (student_id, assignment_id, score) VALUES
(1,1,95),(1,2,45),(1,3,88),(1,4,92),(1,5,140),
(2,1,85),(2,2,40),(2,3,78),(2,4,88),(2,5,130),
(3,1,90),(3,2,48),(3,3,85),(3,4,91),(3,5,142),
(4,1,70),(4,2,35),(4,3,65),(4,4,75),(4,5,120);