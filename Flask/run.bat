call venv/Scripts/activate.bat
set FLASK_APP=student_attendance_tracker
set FLASK_ENV=dev
set FLASK_RUN_HOST=0.0.0.0
set FLASK_RUN_PORT=8080
flask db upgrade
flask run