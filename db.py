from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3

DB_NAME = 'CSE-3.db'
db = sqlite3.connect(DB_NAME)

db.execute('''
	CREATE TABLE IF NOT EXISTS Student(
	register_number INTEGER PRIMARY KEY,
	name TEXT NOT NULL,
	email TEXT UNIQUE NOT NULL,
	password TEXT NOT NULL,
	total_periods INTEGER DEFAULT 0 NOT NULL,
	periods_attended INTEGER DEFAULT 0 NOT NULL);
	''')

db.execute('''
	CREATE TABLE IF NOT EXISTS StudentAttendance(
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	register_number INTEGER NOT NULL,
	date_of_attendance TEXT NOT NULL,
	periods_attended TEXT NOT NULL,
	FOREIGN KEY (register_number) REFERENCES Student (register_number));
	''')

db.commit()
db.close()

def addStudent(register_number, name, email, password):
	try:
		password = generate_password_hash(password)
		db = sqlite3.connect(DB_NAME)
		db.execute('''
		INSERT INTO Student(register_number, name, email, password)
		VALUES('%d', '%s', '%s', '%s');
		''' %(int(register_number), name, email, password))

		db.commit()
		db.close()
		return True
	except:
		return False

def addAttendance(register_number, date_of_attendance, periods_attended):
	db = sqlite3.connect(DB_NAME)
	db.execute('''
	INSERT INTO StudentAttendance(register_number, date_of_attendance, periods_attended)
	VALUES('%d', '%s', '%s');
	''' %(register_number, date_of_attendance, periods_attended))

	db.execute('''
	UPDATE Student
	SET total_periods = total_periods + 8, periods_attended = periods_attended + %d
	WHERE register_number = %d;
	''' %(periodsAttended(periods_attended), register_number))
	
	db.commit()
	db.close()

def viewAttendance(date_of_attendance):
	db = sqlite3.connect(DB_NAME)
	cursor = db.execute('''
	SELECT register_number, date_of_attendance, periods_attended 
	FROM StudentAttendance
    WHERE date_of_attendance = '%s';
	''' %date_of_attendance)
	
	studentAttendance = cursor.fetchall()
	db.close()
	return studentAttendance
	

def verifyStudent(email, password):
	db = sqlite3.connect(DB_NAME)
	cursor = db.execute('''
	SELECT register_number, password
	FROM Student
	WHERE email = '%s';
	''' %email)

	students = cursor.fetchall()
	db.close()
	if students:
		if check_password_hash(students[0][1], password):
			return students[0][0]
	else:
		return False

def getStudentDetails(register_number):
	
	student = {}
	db = sqlite3.connect(DB_NAME)

	cursor = db.execute('''
	SELECT name, email, total_periods, periods_attended
	FROM Student
	WHERE register_number = '%d';
	''' %register_number)

	student['main'] = cursor.fetchall()

	cursor = db.execute('''
	SELECT date_of_attendance, periods_attended 
	FROM StudentAttendance
	WHERE register_number = '%d';
	''' %register_number)

	student['content'] = cursor.fetchall()
	db.close()
	return student

def getAllRegisterNumbers():
	db = sqlite3.connect(DB_NAME)
	cursor = db.execute('''
	SELECT register_number
	FROM Student;
	''')

	allregisternumbers = [element for innerList in cursor.fetchall() for element in innerList]
	db.close()
	allregisternumbers.sort(key = int)
	return allregisternumbers

def periodsAttended(periods_attended):
	count = 0
	for i in periods_attended:
		if i == '1':
			count += 1
	return count
