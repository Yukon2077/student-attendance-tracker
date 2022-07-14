from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session
from db import *
import secrets

app=Flask(__name__)
app.secret_key = secrets.token_hex()

#===================================ROUTING===================================#
#-----------------------------------HOME------------------------------------#
@app.route('/')
def home():
	return render_template("index.html")

#-----------------------------------ABOUT US-----------------------------------#
@app.route('/about-us')
def about_us():
	return render_template("about-us.html")

#-----------------------------------LOGIN-----------------------------------#
@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template("login.html", failure = False)
	else:
		email = request.form['email']
		password = request.form['password']
		if 'staff' in request.form:
			staff_id = verifyStaff(email, password)
			if staff_id:
				session['is_logged_in'] = True
				session['staff_id'] = staff_id
				return redirect(url_for('admin_dashboard'))
			else:
				return render_template("login.html", failure = True)
		else:
			student_id, staff_id = verifyStudent(email, password)
			if student_id:
				session['is_logged_in'] = True
				session['staff_id'] = staff_id
				session['student_id'] = student_id
				return redirect(url_for('student_dashboard', student_id = student_id))
			else:
				return render_template("login.html", failure = True)
		

#-----------------------------------REGISTER-----------------------------------#
@app.route('/register', methods = ['GET', 'POST'])
def register():
	if request.method == 'GET':
		return render_template("register.html", failure = False)
	else:
		name = request.form['name']
		email = request.form['email']
		password = request.form['password']
		staff_id = addStaff(name, email, password)
		if staff_id:
			session['is_logged_in'] = True
			session['staff_id'] = staff_id
			return redirect(url_for('admin_dashboard'))
		else:
			return render_template("register.html", failure = True)
	
#-----------------------------------STAFF DASHBOARD-----------------------------------#
@app.route('/admin')
def admin_dashboard():
	if 'is_logged_in' in session and 'staff_id' in session:
		staff_id = session['staff_id']
		date_of_attendance = datetime.now().strftime('%Y-%m-%d')
		return render_template("admin_dashboard.html", date_of_attendance = date_of_attendance)	
	else:
		return redirect(url_for('login'))

#-----------------------------------ADD STUDENT-----------------------------------#
@app.route('/add_student', methods = ['GET', 'POST'])
def add_student():
	if 'is_logged_in' in session and 'staff_id' in session:
		staff_id = session['staff_id']
		if request.method == 'POST':
			register_number = request.form['register_number']
			name = request.form['name']
			email = request.form['email']
			password = request.form['password']
			result = addStudent(register_number, name, email, password, staff_id)
			if result:
				return render_template("add_student.html", good = True)
			else:
				return render_template("add_student.html", bad = True)
		else:
			return render_template("add_student.html")
	else:
		return redirect(url_for('login'))

#-----------------------------------ADD ATTENDANCE------------------------------------#
@app.route('/add_attendance', methods = ['GET', 'POST'])
def add_attendance():
	if 'is_logged_in' in session and 'staff_id' in session:
		staff_id = session['staff_id']
		date_of_attendance = datetime.now().strftime('%Y-%m-%d')
		students = getStudents(staff_id)
		no_of_periods = int(request.args['no_of_periods'])
		if request.method == 'POST':
			for i in students:
				periods_attended = ''
				for j in range(no_of_periods):
					check = str(i) + '_' + str(j)
					isChecked = check in request.form
					if isChecked:
						periods_attended += '1'
					else:
						periods_attended += '0'
				date_of_attendance = request.form['date_of_attendance']
				addAttendance(staff_id, i[0], date_of_attendance, periods_attended)
			return redirect(url_for('admin_dashboard'))
		else:
			return render_template("add_attendance.html", date_of_attendance = date_of_attendance,
			students = students, no_of_periods = no_of_periods)
	else:
			return redirect(url_for('login'))

#-----------------------------------STUDENT DASHBOARD------------------------------------#
@app.route('/student/<int:student_id>') 
def student_dashboard(student_id):
	if 'is_logged_in' in session and 'student_id' in session:
		student_id = session['student_id']
		student = getStudentDetails(student_id)
		name = student['main'][0][0]
		email = student['main'][0][1]
		total_periods = student['main'][0][2]
		periods_attended = student['main'][0][3]
		attendance = student['content']
		if total_periods != 0:
			percentage = '%.2f' %(periods_attended * 100 /total_periods)
		else:
			percentage = '0.00'
		
		return render_template("student_dashboard.html",
			name = name,
			email = email,
			total_periods = total_periods,
			periods_attended = periods_attended,
			percentage = percentage,
			attendance = attendance)
	else:
		return redirect(url_for('home'))

#-----------------------------------STUDENT DETAILS------------------------------------#
@app.route('/view_attendance')
def view_student_details():
	if 'is_logged_in' in session and 'staff_id' in session:
		staff_id = session['staff_id']
		date_of_attendance = request.args['date_of_attendance']
		attendance = viewAttendance(staff_id, date_of_attendance)
		if len(attendance) > 0:
			no_of_periods = len(attendance[0][3])
		else:
			no_of_periods = 0
		return render_template('view_attendance.html', 
			date_of_attendance = date_of_attendance,
			attendance = attendance,
			no_of_periods = no_of_periods)
	else:
			return redirect(url_for('login'))

#-----------------------------------LOGOUT------------------------------------#
@app.route('/logout')
def logout():
	session.pop('is_logged_in', None)
	session.pop('staff_id', None)
	session.pop('student_id', None)
	return redirect(url_for('login'))

#-----------------------------------STOPS CAHCE------------------------------------#
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return response

#===================================MAIN===================================#
if(__name__ == '__main__'):
	app.run(debug = True, port = 80, host="0.0.0.0")