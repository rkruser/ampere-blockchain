from functools import wraps
from flask import session, request, redirect, url_for, jsonify

"""
Usage:
A class that mediates between the server, the database, and other third party services.

Provides decorators that can be used to wrap around routes for different services like user authentication.

Simplifies the server codebases substantially.

Example:

AM = AuthenticationManager(database=CreateDatabaseInterface(...), third_party=ThirdPartyAuthentication(captcha=CaptchaClient(...)))

@app.route('/login', methods=['POST'])
@AM.captcha_required(failure_response="FAILURE RESPONSE")
def login():
    ...

@app.route('/home', methods=['GET'])
@AM.login_session_required
def home():
    ...

    

TODO:
 - Fix the MFA wrappers
 - Add CSRF support
 - Consider moving the decorators outside the class instance for performance.
 
"""

class AuthenticationManager:
    def __init__(self, database=None, third_party=None):
        self.database = database
        self.third_party = third_party

    def login_user(self, username, password):
        success, session_id = self.database.login_user(username, password)
        if success:
            session['authenticated'] = True
            session['username'] = username
            session['session_id'] = session_id
        return success
    
    def logout_user(self, username, session_id):
        self.database.logout_user(username, session_id)
        session['authenticated'] = False
        session['username'] = None
        session['session_id'] = None

    def login_session_required(self, f, failure_response=None, use_redirect=True, redirect_to='login'):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            session_username = session.get('username', None)
            session_id = session.get('session_id', None)
            if not self.database.verify_user_session(session_username, session_id):
                session['authenticated'] = False # Mainly used in the 2FA wrappers; may have to rethink that
                session['username'] = None
                session['session_id'] = None
                if failure_response:
                    return failure_response, 401
                elif use_redirect:
                    return redirect(url_for(redirect_to))
                return jsonify({'error': 'Not logged in'}), 401
            return f(*args, **kwargs)
        return decorated_function

    def authentication_token_required(self, f, failure_response=None):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', None)
            if not self.database.verify_authentication_token(token):
                return failure_response or jsonify({'error': 'Invalid token'}), 401
            return f(*args, **kwargs)
        return decorated_function
    
    def captcha_required(self, f, failure_response=None):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            captcha = request.form.get('g-recaptcha-response', None)
            if not self.third_party.verify_captcha(captcha):
                return failure_response or jsonify({'error': 'Captcha required'}), 400
            return f(*args, **kwargs)
        return decorated_function

    def csrf_token_required(self, f, failure_response=None):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            csrf_token = request.form.get('csrf_token', None)
            if not self.third_party.verify_csrf_token(csrf_token):
                return failure_response or jsonify({'error': 'Invalid CSRF token'}), 400
            return f(*args, **kwargs)
        return decorated_function

    # The mfa functions still need some work to make them interact with the database
    def send_email_mfa(self, f, failure_response=None):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            email = None
            if session.get('authenticated', False):
                email = self.database.get_user_email(session.get('username', None))
            else:
                email = request.form.get('email', None)

            if not self.third_party.send_email_mfa(email):
                return failure_response or jsonify({'error': 'Could not send authentication email'}), 400
            return f(*args, **kwargs)
        return decorated_function
    
    def verify_email_mfa(self, f, failure_response=None):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            email = None
            if session.get('authenticated', False):
                email = self.database.get_user_email(session.get('username', None))
            else:
                email = request.form.get('email', None)

            code = request.form.get('code', None)
            if not self.third_party.verify_email_mfa(email, code):
                return failure_response or jsonify({'error': 'Invalid authentication code'}), 400
            return f(*args, **kwargs)
        return decorated_function
    
    def send_sms_mfa(self, f, failure_response=None):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            phone_number = None
            if session.get('authenticated', False):
                phone_number = self.database.get_user_phone_number(session.get('username', None))
            else:
                phone_number = request.form.get('phone_number', None)

            if not self.third_party.send_sms_mfa(phone_number):
                return failure_response or jsonify({'error': 'Could not send authentication SMS'}), 400
            return f(*args, **kwargs)
        return decorated_function
    
    def verify_sms_mfa(self, f, failure_response=None):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            phone_number = None
            if session.get('authenticated', False):
                phone_number = self.database.get_user_phone_number(session.get('username', None))
            else:
                phone_number = request.form.get('phone_number', None)

            code = request.form.get('code', None)
            if not self.third_party.verify_sms_mfa(phone_number, code):
                return failure_response or jsonify({'error': 'Invalid authentication code'}), 400
            return f(*args, **kwargs)
        return decorated_function