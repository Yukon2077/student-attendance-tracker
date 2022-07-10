from datetime import datetime
from flask import *
from db import *

app=Flask(__name__)

@app.route('/')
def home():
	return redirect(url_for('login'))

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		email = request.form['usr_email']
		password = request.form['usr_passwd']
		register_number = verifyStudent(email, password)
		if register_number:
			return redirect(url_for('student_dashboard', register_number = register_number), code = 307)
		elif email == 'admin@admin.com' and password == 'admin':
			return redirect(url_for('admin_dashboard'))
		else:
			return render_template("login.html", info = '<p class="alert alert-danger mx-auto text-dark text-center">Invalid email or password</p>')
	else:
		return render_template("login.html")
	
@app.route('/admin')
def admin_dashboard():
	return render_template("admin_dashboard.html")	

@app.route('/add_student', methods = ['GET', 'POST'])
def add_student():
	if request.method == 'POST':
		register_number = request.form['usr_regno']
		name = request.form['usr_name']
		email = request.form['usr_email']
		password = request.form['usr_passwd']
		result = addStudent(register_number, name, email, password)
		if result:
			return render_template("add_student.html", info = 'Student added sucessfully')
		else:
			return render_template("add_student.html", info = 'Some error occured')
	else:
		return render_template("add_student.html")

@app.route('/add_attendance', methods = ['GET', 'POST'])
def add_attendance():
	date_of_attendance = datetime.now().strftime('%Y-%m-%d')
	register_numbers = getAllRegisterNumbers()
	if request.method == 'POST':
		for i in register_numbers:
			periods_attended = ''
			for j in range(8):
				check = str(i) + '_' + str(j)
				isChecked = check in request.form
				if isChecked:
					periods_attended += '1'
				else:
					periods_attended += '0'
			date_of_attendance = request.form['date_of_attendance']
			addAttendance(i, date_of_attendance, periods_attended)
		return render_template("admin_dashboard.html", info = 'Attendance added successfully')
	else:
		return render_template("add_attendance.html", date_of_attendance = date_of_attendance,
		register_numbers = register_numbers)

@app.route('/student/<int:register_number>', methods = ['POST', 'GET']) 
def student_dashboard(register_number):
	if request.method == 'POST':
		student = getStudentDetails(register_number)
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

@app.route('/view_student_details')
def view_student_details():
	date_of_attendance = request.args['date_of_attendance']
	attendance = viewAttendance(date_of_attendance)
	return render_template('view_student.html', 
		date_of_attendance = date_of_attendance,
		attendance = attendance)

if(__name__ == '__main__'):
	app.run(debug = True)