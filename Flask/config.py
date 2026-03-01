import os
from dotenv import load_dotenv
import datetime

basedir = os.path.abspath(os.path.dirname(__file__))
FLASK_ENV = os.getenv('FLASK_ENV', 'dev')
load_dotenv(os.path.join(basedir, 'env', f'{FLASK_ENV}.env'))


class Config:
    FLASK_ENV = FLASK_ENV
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', False)
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS')
    MAIL_SERVER = os.getenv('MAIL_SERVER')
    MAIL_PORT = os.getenv('MAIL_PORT')
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS')
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    UI_BASE_URL = os.getenv('UI_BASE_URL')
    JWT_TOKEN_LOCATION = os.getenv('JWT_TOKEN_LOCATION')
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(
        minutes=int(os.getenv('JWT_ACCESS_TOKEN_EXPIRES'))
    )
    JWT_ACCESS_CSRF_HEADER_NAME = os.getenv('JWT_ACCESS_CSRF_HEADER_NAME')
    JWT_REFRESH_TOKEN_EXPIRES = datetime.timedelta(
        days=int(os.getenv('JWT_REFRESH_TOKEN_EXPIRES'))
    )
    JWT_REFRESH_CSRF_HEADER_NAME = os.getenv('JWT_REFRESH_CSRF_HEADER_NAME')
