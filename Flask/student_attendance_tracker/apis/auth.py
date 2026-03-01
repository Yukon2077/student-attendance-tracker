from flask import current_app, request, make_response
from flask_restx import Namespace, Resource
from flask_mail import Message
from itsdangerous import URLSafeTimedSerializer as Serializer, BadSignature
from flask_jwt_extended import (
    create_access_token,
    set_access_cookies,
    current_user,
    jwt_required,
    get_jwt,
    verify_jwt_in_request,
    unset_access_cookies,
    unset_refresh_cookies,
    set_refresh_cookies,
    create_refresh_token,
)
import re
from datetime import datetime

from student_attendance_tracker import mail, db, bcrypt, jwt
from student_attendance_tracker.models import User, RevokedUserToken
from student_attendance_tracker.constants import ResponseStatus, ResponseCode
from student_attendance_tracker.utilities import create_response


api = Namespace('auth')


@jwt.user_identity_loader
def user_identity_lookup(user):
    return str(user.id)


@jwt.user_lookup_loader
def user_lookup_callback(_jwt_header, jwt_data):
    identity = int(jwt_data['sub'])
    return db.session.execute(db.select(User).filter_by(id=identity)).scalars().first()


@jwt.token_in_blocklist_loader
def check_is_token_is_blocked(jwt_header, jwt_payload: dict):
    user_id = jwt_payload['sub']
    jti = jwt_payload['jti']
    db.session.execute(
        db.delete(RevokedUserToken).where(
            RevokedUserToken.user_id == user_id,
            RevokedUserToken.expires_at < datetime.now(),
        )
    )
    db.session.commit()
    token = db.session.execute(
        db.select(RevokedUserToken).filter_by(user_id=user_id, token=jti)
    ).scalar_one_or_none()
    return token is not None


@api.route('/refresh')
class Refresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        if current_user:
            response = make_response(
                create_response(
                    ResponseStatus.SUCCESS, ResponseCode.SUCCESS, 'Token refreshed'
                ),
                200,
            )
            access_token = str(create_access_token(identity=current_user))
            refresh_token = str(create_refresh_token(identity=current_user))
            set_access_cookies(response, access_token)
            set_refresh_cookies(response, refresh_token)
        return response


@api.route('/fetch_user_session')
class FetchUserSession(Resource):
    @jwt_required(optional=True)
    def get(self):
        if current_user:
            body = {
                'is_authenticated': current_user is not None,
                'name': current_user.name,
                'email': current_user.email,
            }
            return create_response(
                ResponseStatus.SUCCESS, ResponseCode.LOGGED_IN, 'Is logged in!', body
            ), 200
        else:
            return create_response(
                ResponseStatus.ERROR, ResponseCode.NOT_LOGGED_IN, 'Not logged in!'
            ), 400


@api.route('/send_verification_email')
class SendVerificationEmail(Resource):
    def post(self):
        emailDetails = request.get_json()
        email = emailDetails.get('email')
        emailRegex = re.compile(
            r'(?:[a-z0-9!#$%&\'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&\'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])'
        )
        if not bool(re.match(emailRegex, email)):
            return create_response(
                ResponseStatus.ERROR, ResponseCode.EMAIL_NOT_PROPER, 'Email not good!'
            ), 400

        user = db.session.execute(db.select(User).filter_by(email=email)).first()
        if user:
            return create_response(
                ResponseStatus.ERROR,
                ResponseCode.EMAIL_ALREADY_EXISTS,
                'User already exists!',
            ), 400
        serializer = Serializer(current_app.config['SECRET_KEY'])
        token = serializer.dumps(email, salt='hmm, we shall see')
        link = current_app.config['UI_BASE_URL'] + '/verify_email/' + token
        msg = Message(
            'Verify email',
            sender=current_app.config['MAIL_USERNAME'],
            recipients=[email],
            body='You are trying to sign up for Student Attendance Tracker, right? You need to verify your account, so, click this link: '
            + link,
            html='You are trying to sign up for Student Attendance Tracker, right? You need to verify your account, so, click this <a href='
            + link
            + '>link</a>',
        )
        with current_app.app_context():
            mail.send(msg)
        return create_response(
            ResponseStatus.SUCCESS, ResponseCode.VERIFICATION_MAIL_SENT, 'Email sent!'
        ), 200


@api.route('/verify_email')
class VerifyEmail(Resource):
    def post(self):
        try:
            verificationDetails = request.get_json()
            token = verificationDetails.get('token')
            serializer = Serializer(current_app.config['SECRET_KEY'])
            email = serializer.loads(token, max_age=900, salt='hmm, we shall see')

            user = db.session.execute(db.select(User).filter_by(email=email)).first()
            if user:
                return create_response(
                    ResponseStatus.ERROR,
                    ResponseCode.EMAIL_ALREADY_EXISTS,
                    'Email already created!',
                ), 400

            return create_response(
                ResponseStatus.SUCCESS,
                ResponseCode.EMAIL_VERIFIED,
                'Email verified!',
                {'email': email},
            ), 200
        except BadSignature as exception:
            return create_response(
                ResponseStatus.ERROR,
                ResponseCode.BAD_SIGNATURE,
                'Bad Signature!',
                str(exception),
            ), 400
        except Exception as exception:
            return create_response(
                ResponseStatus.ERROR,
                ResponseCode.SOMETHING_WENT_WRONG,
                'Something went wrong!',
                str(exception),
            ), 500


@api.route('/sign_up')
class SignUp(Resource):
    def post(self):
        try:
            signUpDetails = request.get_json()
            encrypted_email = signUpDetails.get('token')
            name = signUpDetails.get('name')
            password = signUpDetails.get('password')
            serializer = Serializer(current_app.config['SECRET_KEY'])
            email = serializer.loads(
                encrypted_email, max_age=900, salt='hmm, we shall see'
            )
            user = db.session.execute(db.select(User).filter_by(email=email)).first()
            if user:
                return create_response(
                    ResponseStatus.ERROR,
                    ResponseCode.EMAIL_ALREADY_EXISTS,
                    'Email already created!',
                ), 400
            if len(name) < 3:
                return create_response(
                    ResponseStatus.ERROR, ResponseCode.NAME_TOO_SHORT, 'Name too short'
                ), 400
            if len(password) < 8:
                return create_response(
                    ResponseStatus.ERROR,
                    ResponseCode.PASSWORD_TOO_SHORT,
                    'Password too short',
                ), 400
            passwordRegex = re.compile(r'(?=.*\d)(?=.*[a-z])(?=.*[A-Z])')
            if not bool(re.match(passwordRegex, password)):
                return create_response(
                    ResponseStatus.ERROR,
                    ResponseCode.PASSWORD_PATTERN_NOT_MATCHED,
                    'Password needs 1 A-Z, a-z and 0-9',
                ), 400
            if email:
                new_user = User(
                    email=email,
                    first_name=name,
                    password=bcrypt.generate_password_hash(password),
                )
                db.session.add(new_user)
                db.session.commit()
                response = make_response(
                    create_response(
                        ResponseStatus.SUCCESS, ResponseCode.SUCCESS, 'Account created!'
                    ),
                    200,
                )
                access_token = str(create_access_token(identity=user))
                refresh_token = str(create_refresh_token(identity=user))
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                return response
        except BadSignature as exception:
            return create_response(
                ResponseStatus.ERROR,
                ResponseCode.BAD_SIGNATURE,
                'Bad Signature!',
                str(exception),
            ), 400


@api.route('/login')
class Login(Resource):
    def post(self):
        loginDetails = request.get_json()
        email = loginDetails.get('email')
        password = loginDetails.get('password')
        user = (
            db.session.execute(db.select(User).filter_by(email=email)).scalars().first()
        )
        if user:
            if bcrypt.check_password_hash(user.password, password):
                response = make_response(
                    create_response(
                        ResponseStatus.SUCCESS, ResponseCode.LOGGED_IN, 'Logged in!'
                    ),
                    200,
                )
                access_token = str(create_access_token(identity=user))
                refresh_token = str(create_refresh_token(identity=user))
                set_access_cookies(response, access_token)
                set_refresh_cookies(response, refresh_token)
                return response
            return create_response(
                ResponseStatus.ERROR,
                ResponseCode.PASSWORD_INCORRECT,
                'Password incorrect',
            ), 400
        else:
            return create_response(
                ResponseStatus.ERROR,
                ResponseCode.EMAIL_DOES_NOT_EXISTS,
                "Email doesn't exist",
            ), 400


@api.route('/logout')
class Logout(Resource):
    @jwt_required(verify_type=False)
    def post(self):
        response = make_response(
            create_response(
                ResponseStatus.SUCCESS, ResponseCode.LOGGED_OUT, 'Logged out!'
            ),
            200,
        )
        if current_user:
            access_jwt = get_jwt()
            revoked_access_token = RevokedUserToken()
            revoked_access_token.user_id = current_user.id
            revoked_access_token.token = access_jwt['jti']
            revoked_access_token.type = access_jwt['type'].upper()
            revoked_access_token.expires_at = datetime.fromtimestamp(access_jwt['exp'])
            db.session.add(revoked_access_token)
            verify_jwt_in_request(refresh=True)
            refresh_jwt = get_jwt()
            revoked_refresh_token = RevokedUserToken()
            revoked_refresh_token.user_id = current_user.id
            revoked_refresh_token.token = refresh_jwt['jti']
            revoked_refresh_token.type = refresh_jwt['type'].upper()
            revoked_refresh_token.expires_at = datetime.fromtimestamp(
                refresh_jwt['exp']
            )
            db.session.add(revoked_refresh_token)
            db.session.commit()
            unset_access_cookies(response)
            unset_refresh_cookies(response)
        return response
