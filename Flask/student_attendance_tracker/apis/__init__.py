from .auth import api as auth
from flask import Blueprint
from flask_restx import Api
from student_attendance_tracker.constants import ResponseStatus, ResponseCode
from student_attendance_tracker.utilities import create_response


blueprint = Blueprint('api', __name__)
api = Api(blueprint)
api.add_namespace(auth)

@api.errorhandler(Exception)
def default_error_handler(error):
    return create_response(ResponseStatus.ERROR, ResponseCode.SOMETHING_WENT_WRONG, 'Something went wrong!', str(error)), 500