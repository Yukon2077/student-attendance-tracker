from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

DB_NAME = 'database.db'
db = sqlite3.connect(DB_NAME)

#===================================CREATING TABLES===================================#
#-----------------------------------STAFF------------------------------------#
db.execute('''
	CREATE TABLE IF NOT EXISTS Staff(
	staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	email TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL);
	''')

#-----------------------------------STUDENT------------------------------------#
db.execute('''
	CREATE TABLE IF NOT EXISTS Student(
	student_id INTEGER PRIMARY KEY AUTOINCREMENT,
	staff_id INTEGER NOT NULL,
	register_number TEXT NOT NULL,
	name TEXT NOT NULL,
	email TEXT NOT NULL,
	password TEXT NOT NULL,
	total_periods INTEGER DEFAULT 0 NOT NULL,
	periods_attended INTEGER DEFAULT 0 NOT NULL,
	FOREIGN KEY (staff_id) REFERENCES Staff (staff_id),
	UNIQUE (staff_id, register_number));
	''')

#-----------------------------------STUDENT ATTENDANCE------------------------------------#
db.execute('''
	CREATE TABLE IF NOT EXISTS StudentAttendance(
	attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
	staff_id INTEGER NOT NULL,
	student_id INTEGER NOT NULL,
	date_of_attendance TEXT NOT NULL,
	periods_attended TEXT NOT NULL,
	FOREIGN KEY (student_id) REFERENCES Student (student_id),
	FOREIGN KEY (staff_id) REFERENCES Staff (staff_id));
	''')

db.commit()
db.close()

#===================================CREATE===================================#
#-----------------------------------STAFF------------------------------------#
def addStaff(name, email, password):
	password = generate_password_hash(password)
	db = sqlite3.connect(DB_NAME)

	db.execute('''
	INSERT INTO Staff(name, email, password)
	VALUES('%s', '%s', '%s');
	''' %(name, email, password))

	db.commit()

	cursor = db.execute('''
	SELECT staff_id FROM Staff WHERE email = '%s' 
	''' %email)
	
	staff_id = cursor.fetchall()
	db.close()
	return staff_id[0][0]

#-----------------------------------STUDENT------------------------------------#
def addStudent(register_number, name, email, password, staff_id):
	password = generate_password_hash(password)
	db = sqlite3.connect(DB_NAME)

	db.execute('''
	INSERT INTO Student(staff_id, register_number, name, email, password)
	VALUES('%d', '%s', '%s', '%s', '%s');
	''' %(int(staff_id), register_number, name, email, password))

	db.commit()
	db.close()
	return True

#-----------------------------------STUDENT ATTENDANCE------------------------------------#
def addAttendance(staff_id, student_id, date_of_attendance, periods_attended):
	db = sqlite3.connect(DB_NAME)

	db.execute('''
	INSERT INTO StudentAttendance(staff_id, student_id, date_of_attendance, periods_attended)
	VALUES('%d', '%d', '%s', '%s');
	''' %(staff_id, student_id, date_of_attendance, periods_attended))

	db.execute('''
	UPDATE Student
	SET total_periods = total_periods + 8, periods_attended = periods_attended + %d
	WHERE student_id = %d;
	''' %(periodsAttended(periods_attended), student_id))
	
	db.commit()
	db.close()

#===================================READ===================================#
#-----------------------------------STUDENT ATTENDANCE------------------------------------#
def viewAttendance(staff_id, date_of_attendance):
	db = sqlite3.connect(DB_NAME)

	cursor = db.execute('''
	SELECT S.register_number, S.name, SA.date_of_attendance, SA.periods_attended 
	FROM Student AS S INNER JOIN StudentAttendance AS SA
	ON S.student_id = SA.student_id
    WHERE SA.staff_id = '%d' AND SA.date_of_attendance = '%s';
	''' %(staff_id, date_of_attendance))
	
	studentAttendance = cursor.fetchall()
	db.close()
	return studentAttendance
	
#-----------------------------------STUDENT------------------------------------#
def verifyStudent(email, password):
	db = sqlite3.connect(DB_NAME)

	cursor = db.execute('''
	SELECT student_id, password, staff_id
	FROM Student
	WHERE email = '%s';
	''' %email)

	students = cursor.fetchall()
	db.close()
	if students:
		if check_password_hash(students[0][1], password):
			return (students[0][0], students[0][2])
	else:
		return False

def getStudentDetails(student_id):
	
	student = {}
	db = sqlite3.connect(DB_NAME)

	cursor = db.execute('''
	SELECT name, email, total_periods, periods_attended
	FROM Student
	WHERE student_id = '%d';
	''' %student_id)

	student['main'] = cursor.fetchall()

	cursor = db.execute('''
	SELECT date_of_attendance, periods_attended 
	FROM StudentAttendance
	WHERE student_id = '%d';
	''' %student_id)

	student['content'] = cursor.fetchall()
	db.close()
	return student

#-----------------------------------STAFF------------------------------------#
def verifyStaff(email, password):
	db = sqlite3.connect(DB_NAME)

	cursor = db.execute('''
	SELECT staff_id, email, password
	FROM Staff
	WHERE email = '%s';
	''' %email)

	staffs = cursor.fetchall()
	db.close()
	if staffs:
		if check_password_hash(staffs[0][2], password):
			return staffs[0][0]
	else:
		return False

def getStaffDetails(staff_id):
	db = sqlite3.connect(DB_NAME)

	cursor = db.execute('''
	SELECT name, email, no_of_students
	FROM Staff
	WHERE staff_id = '%d';
	''' %staff_id)

	staff = cursor.fetchall()
	db.close()
	return staff

def getStudents(staff_id):
	db = sqlite3.connect(DB_NAME)

	cursor = db.execute('''
	SELECT student_id, register_number, name
	FROM Student
	WHERE staff_id = '%d'
	ORDER BY register_number;
	''' %staff_id)

	allregisternumbers = cursor.fetchall()
	db.close()
	return allregisternumbers

def periodsAttended(periods_attended):
	count = 0
	for i in periods_attended:
		if i == '1':
			count += 1
	return count