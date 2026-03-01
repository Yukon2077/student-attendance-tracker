from flask import Flask, current_app
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_mail import Mail
from flask_bcrypt import Bcrypt
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from .utilities import Base

db = SQLAlchemy(model_class=Base)
migrate = Migrate()
mail = Mail()
bcrypt = Bcrypt()
jwt = JWTManager()
cors = CORS()


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    migrate.init_app(app, db)
    mail.init_app(app)
    bcrypt.init_app(app)
    jwt.init_app(app)
    cors.init_app(
        app,
        supports_credentials=True,
        resources={r'/api/*': {'origins': app.config['UI_BASE_URL']}},
    )

    from student_attendance_tracker.apis import blueprint as api

    app.register_blueprint(api, url_prefix='/api')

    @app.route('/')
    def index():
        return current_app.config['FLASK_ENV']

    return app
