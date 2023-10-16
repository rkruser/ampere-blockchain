from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import database as db
import security as sec
import ssl
import argparse
import json
from datetime import datetime, timedelta
import requests
import functools
import email_2fa as mail

#from flask_recaptcha import ReCaptcha





"""
To Do:

0. Improve web pages on server to make them more navigable
1. Persist flask server secret key in database (and persist database)
2. Store logged in session keys mapped to the identity of the flask server secret key used to generate them (such as the hash of that key). If a client provides session keys not mapped to current secret key, make them log in again. (*Actually, may not be necessary, since flask won't be able to decrypt the old session keys with the new secret key anyway)
3. Persist session cookies and usernames/passwords on client side.
4. Add CSRF tokens for individual sessions/post requests (mainly for browser security to prevent post requests made by other sites)
5. Set cookie flags for maximum security, and define an explicit content-security-policy (CSP) with whitelisting. (Again, mainly for browser security.)

6. Add "prove you're human" stuff to registration page (how would automatic app registration deal with this? Invitation codes? Make app instances only able to login, not to register?)

7. Then, more stuff with ZMQ networking



----

Add logout success and registration success intermediate pages
Add the csrf stuff to the non-login forms
Add sendgrid 2FA to registration page
Add prove you're human to registration page
(Limit number of registration attempts per IP address)


----

Consider removing javascript from login form and other forms
NOTE: login protections apparently don't work on the files in "static"; don't put secrets in static folder



"""



app = Flask(__name__)
app.secret_key = sec.generate_session_key()

app.config['RECAPTCHA_SITE_KEY'] = '6LeT5JwoAAAAAIDvqRrzCMQUteRFtSSvuAAOAdzQ'
app.config['RECAPTCHA_SECRET_KEY'] = '6LeT5JwoAAAAAJwDW1aLS-Ss65ZJJabvnO6hqKA5'
#recaptcha = ReCaptcha(app=app)

# Site key: 6LeT5JwoAAAAAIDvqRrzCMQUteRFtSSvuAAOAdzQ
# Secret key: 6LeT5JwoAAAAAJwDW1aLS-Ss65ZJJabvnO6hqKA5



default_csp = ("default-src 'self'; "  # By default, only load resources from the same origin
              "script-src 'self' code.jquery.com cdnjs.cloudflare.com www.google.com www.gstatic.com; "  # Whitelist CDN for scripts
              "style-src 'self' cdn.styles.com; "  # Whitelist CDN for styles
              "img-src 'self' cdn.images.com; "  # Whitelist CDN for images
              "font-src *.fonts.com;"  # Allow fonts from any subdomain under fonts.com
              "frame-src www.google.com; " # Whitelist recaptcha
             )


@app.after_request
def add_csp_headers(response):
    response.headers['Content-Security-Policy'] = default_csp
    return response



@app.before_request
def require_login():
    username, status = verify_session()
    if status != "success" and request.endpoint not in ['login', 'register', 'static', 'complete_registration']:
        return redirect(url_for('login'))




db.add_invitation("basic_invite")
db.add_user("user1", "password1")

db.add_user("admin", "password", permission_level="admin")

@app.route('/', methods=['GET', 'POST'])
def index():
    username = session['username']
    welcome_message = f'Welcome home, {username}!'

    if request.method == 'GET':
        return render_template('index.html', welcome_message=welcome_message)
    
    return jsonify({"message": welcome_message}), 200

@app.route('/home', methods=['GET', 'POST'])
def home():
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        #return render_template('register.html', recaptcha=recaptcha())
        return render_template('register.html')

    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    invitation_code = request.json.get('invitation_code')

    captcha_token = request.json.get('g-recaptcha-response')
    #print("captcha_token:", captcha_token)

    # Use the requests library to query the recaptcha API with a post request
    try:
        response = requests.post('https://www.google.com/recaptcha/api/siteverify', 
                                data={'secret': app.config['RECAPTCHA_SECRET_KEY'], 
                                    'response': captcha_token,
                                    'remoteip': request.remote_addr},
                                    timeout=10)
    except requests.exceptions.Timeout:
        return jsonify({"message": "Recaptcha timed out"}), 401
    
    #print(response.json())

    # Check if the recaptcha was successful
    if not response.json().get('success'):
        return jsonify({"message": "Recaptcha failed"}), 401

    # Check if the invitation code is valid
    if not db.verify_invitation(invitation_code):
        return jsonify({"message": "Invalid invitation code"}), 401

    # Register the user
    try:
        temp_user_id, code = db.add_temp_user(username, password)
    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    
    if not mail.send_email([email], "Verify your email address", f"Your verification code is {code}"):
        return jsonify({"message": "Error sending email"}), 401

    return jsonify({"message": "Registration started. Redirecting...", "redirect_url": url_for('complete_registration', temp_user_id=temp_user_id)}), 200


#@app.route('/complete-registration/', defaults={'temp_user_id': None}, methods=['GET', 'POST'])
@app.route('/complete-registration/<temp_user_id>', methods=['GET', 'POST'])
def complete_registration(temp_user_id):
    #print("Here in complete registration")
    if request.method == 'GET':
        #print("here in get ", temp_user_id)
        return render_template('complete_registration.html', temp_id=temp_user_id)
    temp_user_id = request.json.get('temp_id')
    user_code_input = request.json.get('code')
    if not db.verify_and_add_temp_user(temp_user_id, user_code_input):
        return jsonify({"message": "Invalid or expired user code"}), 401
    return jsonify({"message": "Registration success! Please log in."}), 200


@app.route('/login', methods=['GET', 'POST'])
def login():
    username = session.get('username', None)
    if username is not None:
        return jsonify({"message": f"Already logged in as {username}; please logout first if you want to login to a different account."}), 200

    if request.method == 'GET':
        return render_template('login.html')

    username = request.json.get('username')
    password = request.json.get('password')
    client_ip = request.remote_addr
    # Login the user
    try:
        session_key = db.login_user(username, password, client_ip)
    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    # Set the session key in the session
    app.config['SESSION_COOKIE_SECURE'] = True #Set cookie flags for maximum security
    app.config['SESSION_COOKIE_HTTPONLY'] = True
    app.config['SESSION_COOKIE_SAMESITE'] = 'Strict'
    #app.config['SESSION_PERMANENT'] = True #Persist session cookies
    #app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1) #Persist session cookies for 1 hour
    
    # Note! You need to set the session permanency as follows, not as above. Perhaps it is mainly because you need to use
    #  the session.permanent object, not the app.config object, to set permanency.
    # Also, need to be within a request context to set the session.permanent object, I think
    session.permanent = True
    app.permanent_session_lifetime = timedelta(days=1)
    
    session['username'] = username
    session['session_key'] = session_key
    return jsonify({"message": "Login success!"}), 200

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session_key = session.get('session_key', None)
    status = db.logout_user(session_key)
    session.pop('session_key', None) # Remove the session key from the flask server session
    session.pop('username', None) # Remove the username from the flask server session
    message = None
    if not status:
        message = "Already logged out"
    else:
        message = "Logout success"

    if request.method == 'GET':
        return render_template('logout.html', message=message)
    
    return jsonify({"message": message}), 200

def verify_session():
    session_key = session.get('session_key', None)
    session_username = session.get('username', None)
    if session_key is None:
        return None, "Not logged in"
    client_ip = request.remote_addr
    username = db.verify_session_key(client_ip, session_key)
    if username is None:
        return None, "Session expired or invalid"
    if username != session_username:
        return None, "Session username does not match session key"
    return username, "success"




def add_csrf_token_to_session(minutes_to_expiration=15):
    token = sec.generate_csrf_token()
    expiration_time = datetime.utcnow() + timedelta(minutes=minutes_to_expiration)
    session['csrf_token'] = token
    session['csrf_token_expires'] = expiration_time.strftime('%Y-%m-%dT%H:%M:%SZ')  # ISO 8601 format
    return token

# Can delete tokens for the form to have a single use
def verify_csrf_token(user_provided_token, delete=False):
    if 'csrf_token' not in session:
        return False, "CSRF token not found in session, reload page"
    if 'csrf_token_expires' not in session:
        return False, "CSRF token expiration time not found in session, reload page"
    if datetime.utcnow() > datetime.strptime(session['csrf_token_expires'], '%Y-%m-%dT%H:%M:%SZ'):
        del session['csrf_token']
        del session['csrf_token_expires']
        return False, "CSRF token expired, reload page"
    if user_provided_token != session['csrf_token']:
        del session['csrf_token']
        del session['csrf_token_expires']
        return False, "CSRF token invalid, reload page"
    if delete:
        del session['csrf_token']
        del session['csrf_token_expires']
    return True, "success"

@app.route('/get_csrf_token', methods=['GET'])
def get_csrf_token():
    token = add_csrf_token_to_session()
    return jsonify({"csrf_token": token}), 200


@app.route('/add_user_license', methods=['GET', 'POST'])
def add_user_license():
    username = session['username']
    
    if request.method == 'GET':
        return render_template('add_user_license.html', username=username, csrf_token=add_csrf_token_to_session())

    csrf_token = request.json.get('csrf_token')
    status, message = verify_csrf_token(csrf_token)
    if not status:
        return jsonify({"message": message}), 401

    license_name = request.json.get('license_name')

    try:
        db.add_user_license(username, license_name)
    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    return jsonify({"message": f"Added license {license_name} to {username}'s account."}), 200



@app.route('/request_api_key', methods=['GET', 'POST'])
def request_api_key():
    username = session['username']
    
    if request.method == 'GET':
        return render_template('request_api_key.html', username=username, csrf_token=add_csrf_token_to_session())

    csrf_token = request.json.get('csrf_token')
    status, message = verify_csrf_token(csrf_token)
    if not status:
        return jsonify({"message": message}), 401
    
    license_name = request.json.get('license_name')

    try:
        api_key = db.request_api_key(username, license_name)
        api_key_hash = sec.hash_api_key_truncate_64(api_key)
        print(api_key)
        print(type(api_key))
    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    return jsonify({"message": f"Successfully added API key under license {license_name} to {username}'s account.",
                    "api_key": api_key,
                    "api_key_hash":api_key_hash}), 200

@app.route('/activate_api_key', methods=['GET', 'POST'])
def activate_api_key():
    username = session['username']
    
    if request.method == 'GET':
        return render_template('activate_api_key.html', username=username, csrf_token=add_csrf_token_to_session())

    csrf_token = request.json.get('csrf_token')
    status, message = verify_csrf_token(csrf_token)
    if not status:
        return jsonify({"message": message}), 401

    api_key = request.json.get('api_key')
    #client_ip = request.remote_addr
    client_lan_ip = request.json.get('lan_ip_address')
    client_remote_ip = request.json.get('remote_ip_address')
    node_port = request.json.get('node_port')
    public_key = request.json.get('public_key')
    data = None
    if (public_key is not None) and (node_port is not None):
        data = {"lan_ip_address": client_lan_ip,
                "remote_ip_address": client_remote_ip,
                "port": node_port,
                "public_key": public_key}

    try:
        db.activate_api_key(username, api_key, data=data)
    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    return jsonify({"message": "Successfully activated API key"}), 200


@app.route('/get_node_database', methods=['GET', 'POST'])
def get_node_database():    
    return jsonify({"message": "Here are the nodes!",
                    "node_database": db.node_database,
                    }), 200


@app.route('/server_status', methods=['GET', 'POST'])
def server_status():
    username = session['username']
    
    if not db.has_admin_permissions(username):
        return jsonify({"message": "You do not have permission to view this page"}), 401
    
    server_data = {"message": "Server is up!",
                    "invitation_database": db.convert_sets_to_lists(db._invitation_database),
                    "user_database": db.convert_sets_to_lists(db._user_database),
                    "session_database": db.convert_sets_to_lists(db._session_database),
                    "license_database": db.convert_sets_to_lists(db.license_database),
                    "api_key_database": db.convert_sets_to_lists(db._api_key_database),
                    "node_database": db.node_database
                    }

    if request.method == 'GET':
        pretty_json = json.dumps(server_data, indent=4)
        #escaped_json = html.escape(pretty_json) #no need for this since flask auto-escapes
        return render_template('server_status.html', server_status=pretty_json)

    return jsonify(server_data), 200


@app.route('/visualize')
def visualize():    
    graph_data = db.convert_to_cytoscape_data(db.node_database)
    return render_template('visualize.html', graph_data=graph_data)

@app.route('/userlist')
def user_list():    
    user_data = db.preprocess_user_data(db._user_database)
    return render_template('userlist.html', user_data=user_data)



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--use_ssl', action='store_true')
    args = parser.parse_args()

    if args.use_ssl:
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) #Change to v1_3 when available
        context.load_cert_chain(certfile='C:/Certbot/live/ryenandvivekstartup.online/fullchain.pem', 
                                keyfile='C:/Certbot/live/ryenandvivekstartup.online/privkey.pem')
        #context.verify_mode = ssl.CERT_OPTIONAL

        app.run(ssl_context=context, host='0.0.0.0', debug=True, port=3000)

    else:
        app.run(host='127.0.0.1', debug=True, port=3333)