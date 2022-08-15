from datetime import datetime
from flask import Flask, render_template, redirect, url_for, request, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
app.secret_key = secrets.token_hex()

#===================================MODELS===================================#
#-----------------------------------STAFF------------------------------------#
class Staff(db.Model):
	staff_id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String, nullable = False)
	email = db.Column(db.String, nullable = False, unique = True)
	password = db.Column(db.String, nullable = False)
	students = db.relationship('Student', backref = 'staff')
	attendences = db.relationship('Attendance', backref = 'staff')
#-----------------------------------STUDENT------------------------------------#
class Student(db.Model):
	__table_args__ = (db.UniqueConstraint('staff_id', 'register_number'),
		db.UniqueConstraint('staff_id', 'email'))
	student_id = db.Column(db.Integer, primary_key = True)
	staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable = False)
	register_number = db.Column(db.String, nullable = False)
	name = db.Column(db.String, nullable = False)
	email = db.Column(db.String, nullable = False)
	password = db.Column(db.String, nullable = False)
	total_periods = db.Column(db.Integer, nullable = False, default = 0)
	total_periods_attended = db.Column(db.Integer, nullable = False, default = 0)
	attendences = db.relationship('Attendance', backref = 'student')
#-----------------------------------ATTENDANCE------------------------------------#
class Attendance(db.Model):
	__table_args__ = (db.UniqueConstraint('student_id', 'date_of_attendance'),)
	attendance_id = db.Column(db.Integer, primary_key = True)
	student_id = db.Column(db.Integer, db.ForeignKey('student.student_id'), nullable = False)
	staff_id = db.Column(db.Integer, db.ForeignKey('staff.staff_id'), nullable = False)
	date_of_attendance = db.Column(db.String, nullable = False)
	periods_attended = db.Column(db.String, nullable = False)

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
			staff = Staff.query.filter_by(email = email).first()
			if staff and check_password_hash(staff.password, password):
				session['is_logged_in'] = True
				session['staff_id'] = staff.staff_id
				return redirect(url_for('admin_dashboard'))
			else:
				return render_template("login.html", failure = True)
		else:
			student = Student.query.filter_by(email = email).first()
			if student and check_password_hash(student.password, password):
				session['is_logged_in'] = True
				session['student_id'] = student.student_id
				return redirect(url_for('student_dashboard'))
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
		password = generate_password_hash(request.form['password'])
		staff = Staff(name = name, email = email, password = password)
		db.session.add(staff)
		db.session.commit()
		if staff.staff_id:
			session['is_logged_in'] = True
			session['staff_id'] = staff.staff_id
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
			password = generate_password_hash(request.form['password'])
			student = Student(register_number = register_number, 
				name = name, 
				email = email, 
				password = password, 
				staff_id = staff_id)
			db.session.add(student)
			db.session.commit()
			if student.student_id:
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
		students = Student.query.filter_by(staff_id = staff_id).order_by(Student.register_number).all()
		no_of_periods = int(request.args['no_of_periods'])
		if request.method == 'POST':
			for i in students:
				periods_attended = ''
				for j in range(no_of_periods):
					check = str(i.student_id) + '_' + str(j)
					isChecked = check in request.form
					if isChecked:
						periods_attended += '1'
					else:
						periods_attended += '0'
				date_of_attendance = request.form['date_of_attendance']
				attendance = Attendance(student_id = i.student_id,
					staff_id = staff_id,
					date_of_attendance = date_of_attendance, 
					periods_attended = periods_attended)
				db.session.add(attendance)
			db.session.commit()
			return redirect(url_for('admin_dashboard'))
		else:
			return render_template("add_attendance.html", 
				date_of_attendance = date_of_attendance,
				students = students, 
				no_of_periods = no_of_periods)
	else:
			return redirect(url_for('login'))

#-----------------------------------STUDENT DASHBOARD------------------------------------#
@app.route('/student') 
def student_dashboard():
	if 'is_logged_in' in session and 'student_id' in session:
		student_id = session['student_id']
		student = Student.query.filter_by(student_id = student_id).first()
		attendance = Attendance.query.filter_by(student_id = student_id).all()
		no_of_periods = 0
		for i in attendance:
			if no_of_periods < len(i.periods_attended):
				no_of_periods = len(i.periods_attended)
		return render_template("student_dashboard.html",
			student = student,
			attendance = attendance,
			no_of_periods = no_of_periods)
	else:
		return redirect(url_for('login'))

#-----------------------------------STUDENT DETAILS------------------------------------#
@app.route('/view_attendance')
def view_student_details():
	if 'is_logged_in' in session and 'staff_id' in session:
		staff_id = session['staff_id']
		date_of_attendance = request.args['date_of_attendance']
		attendance = Attendance.query.join(Student).filter(Attendance.student_id == Student.student_id, Attendance.date_of_attendance == date_of_attendance).order_by(Student.register_number).all()
		if len(attendance) > 0:
			no_of_periods = len(attendance[0].periods_attended)
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
	db.create_all()
	app.run(debug = True, port = 80, host="0.0.0.0")