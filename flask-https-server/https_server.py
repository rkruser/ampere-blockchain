from flask import Flask, request, jsonify, session
import database as db
import security as sec

app = Flask(__name__)
app.secret_key = sec.generate_session_key()

db.add_invitation("basic_invite")
db.add_user("user1", "password1")

db.add_user("admin", "password", permission_level="admin")

@app.route('/')
def index():
    return "Hello, this is an https server!"

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    password = request.json.get('password')
    invitation_code = request.json.get('invitation_code')

    # Check if the invitation code is valid
    if not db.verify_invitation(invitation_code):
        return jsonify({"message": "Invalid invitation code"}), 401

    # Register the user
    try:
        db.add_user(username, password)
    except ValueError as e:
        return jsonify({"message": str(e)}), 401

    return jsonify({"message": "Registration success! Please login."}), 200

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    client_ip = request.remote_addr
    # Login the user
    try:
        session_key = db.login_user(username, password, client_ip)
    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    # Set the session key in the session
    session['session_key'] = session_key
    return jsonify({"message": "Login success!"}), 200

@app.route('/logout', methods=['GET', 'POST'])
def logout():
    session_key = session.get('session_key', None)
    status = db.logout_user(session_key)
    session.pop('session_key', None) # Remove the session key from the flask server session
    if not status:
        return jsonify({"message": "Already logged out."}), 200
    return jsonify({"message": "Logout success!"}), 200

def verify_session():
    session_key = session.get('session_key', None)
    if session_key is None:
        return None, "Not logged in"
    client_ip = request.remote_addr
    username = db.verify_session_key(client_ip, session_key)
    if username is None:
        return None, "Session expired or invalid"
    return username, "success"

@app.route('/home', methods=['GET', 'POST'])
def home():
    username, status = verify_session()
    if status != "success":
        return jsonify({"message": status}), 401

    return jsonify({"message": f"Welcome home, {username}!"}), 200

@app.route('/server_status', methods=['GET', 'POST'])
def server_status():
    username, status = verify_session()
    if status != "success":
        return jsonify({"message": status}), 401
    
    if not db.has_admin_permissions(username):
        return jsonify({"message": "You do not have permission to view this page"}), 401
    
    return jsonify({"message": "Server is up!",
                    "invitation_database": db.convert_sets_to_lists(db._invitation_database),
                    "user_database": db.convert_sets_to_lists(db._user_database),
                    "session_database": db.convert_sets_to_lists(db._session_database),
                    "license_database": db.convert_sets_to_lists(db.license_database),
                    "api_key_database": db.convert_sets_to_lists(db._api_key_database)
                    }), 200

if __name__ == '__main__':
    # These paths should really be in a .env file that is configured to the host computer
    app.run(ssl_context=('C:/Certbot/live/ryenandvivekstartup.online/fullchain.pem', 
                         'C:/Certbot/live/ryenandvivekstartup.online/privkey.pem'), 
                         host='0.0.0.0', 
                         debug=True, 
                         port=3000)