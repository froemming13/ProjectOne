# author: T. Urness and M. Moore
# description: Flask example using redirect, url_for, and flash
# credit: the template html files were constructed with the help of ChatGPT

from flask import Flask
from flask import render_template
from flask import Flask, render_template, request, redirect, url_for, flash
from dbCode import *

app = Flask(__name__)
app.secret_key = 'your_secret_key' # this is an artifact for using flash displays; 
                                   # it is required, but you can leave this alone

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        # extract form data
        name = request.form['name']
        email = request.form['email']
        grade_level = request.form['grade_level']
        
        # adding student to DynamoDB
        try:
            new_id = add_student_to_db(name, email, grade_level)        
            flash(f'New Student Added! ID: {new_id}', 'success')  # 'success' is a category; makes a green banner at the top
        
        except Exception as e:
            flash(f"An error occured while adding the student, please enter a valid integer: {str(e)}", 'danger')
        
        # redirect to home page or another page upon successful submission
        return redirect(url_for('home'))
    else:
        # render the form page if the request method is GET
        return render_template('add_user.html')

@app.route('/delete-student',methods=['GET', 'POST'])
def delete_student():
    if request.method == 'POST':
        # extract form data
        try:
            student_id = int(request.form['student_id'])

        except (ValueError, KeyError):
            flash("Please enter a valid Student ID.", 'danger')
            return redirect(url_for('delete_student'))
        
        # attempts to delete student
        try:
            success = delete_student_from_db(student_id)
            # message based on results
            if success:
                flash(f'Student {student_id} deleted!', 'success')
            else:
                flash(f'Student ID {student_id} not found', 'danger')
        
        except Exception as e:
            flash(f"An error occured while deleting the student: {str(e)}",'danger')
        
        return redirect(url_for('home'))
    else:
        # render the form page if the request method is GET
        return render_template('delete_user.html')

@app.route('/update-grades', methods=['GET', 'POST'])
def update_grades():
    if request.method == 'POST':
        # grabs form data and converts it
        try:
            student_id = int(request.form['student_id'])
            assignment_id = int(request.form['assignment_id'])
            new_score = int(request.form['score'])
        except (ValueError, KeyError):
            flash("Please enter valid numeric values for student, assignment, and score.", 'danger')
            return redirect(url_for('update_grades'))
        
        # enforcing valid assignment IDs (only 1-5 allowed)
        if assignment_id not in [1, 2, 3, 4, 5]:
            flash("Invalid assignment ID. Only 1-5 are allowed.", 'danger')
            return redirect(url_for('home'))
        
        # update student grade
        success = update_student_grades_db(student_id, assignment_id, new_score)

        # show appropriate result message
        if success:
            flash('Grade updated successfully!', 'success')
        else:
            flash('Student or assignment not found.', 'danger')

        # redirect to home page
        return redirect(url_for('home'))
    
    # show the form
    return render_template('update_grades.html')

@app.route('/display-students')
def display_students():
    students = get_all_students()
    # if no students found and returned set to empty list
    if students is None:
        students = []
    # render page with student data
    return render_template('display_users.html', users = students)

@app.route('/low-grades', methods=['GET','POST'])
def low_grades():
    if request.method == 'POST':
        try:
        # get threshold from form and ensure it is an integer
            threshold = float(request.form['threshold'])
        except (ValueError, KeyError):
            return render_template('low_grades_form.html', error = "Please enter a valid number.")
        # grab students with grades below the threshold
        results = get_low_grades(threshold)
        # render the results
        return render_template('low_grades.html', results=results)
    
    # show input form
    return render_template('low_grades_form.html')

@app.route('/students_average')
def average_grade():
    results = get_average_grade()
    # render results page with averages
    return render_template('students_average.html', results=results)
    
# these two lines of code should always be the last in the file
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
