from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import database as db
import security as sec
import ssl


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

"""



app = Flask(__name__)
app.secret_key = sec.generate_session_key()

db.add_invitation("basic_invite")
db.add_user("user1", "password1")

db.add_user("admin", "password", permission_level="admin")

@app.route('/', methods=['GET', 'POST'])
def index():
    username, status = verify_session()
    welcome_message = 'Welcome to the homepage!'
    if status == "success":
        welcome_message = f'Welcome home, {username}!'

    if request.method == 'GET':
        return render_template('index.html', welcome_message=welcome_message)
    
    return jsonify({"message": welcome_message}), 200

@app.route('/home', methods=['GET', 'POST'])
def home():
    return redirect(url_for('index'))

@app.route('/register', methods=['Get', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

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

@app.route('/login', methods=['GET', 'POST'])
def login():
    username, status = verify_session()
    if status == "success":
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

@app.route('/add_user_license', methods=['GET', 'POST'])
def add_user_license():
    username, status = verify_session()
    if status != "success":
        return jsonify({"message": status}), 401
    
    if request.method == 'GET':
        return render_template('add_user_license.html', username=username)

    license_name = request.json.get('license_name')
    try:
        db.add_user_license(username, license_name)
    except ValueError as e:
        return jsonify({"message": str(e)}), 401
    return jsonify({"message": f"Added license {license_name} to {username}'s account."}), 200

@app.route('/request_api_key', methods=['GET', 'POST'])
def request_api_key():
    username, status = verify_session()
    if status != "success":
        return jsonify({"message": status}), 401
    
    if request.method == 'GET':
        return render_template('request_api_key.html', username=username)

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
    username, status = verify_session() #Someone has to be logged in, doesn't matter who
    if status != "success":
        return jsonify({"message": status}), 401
    
    if request.method == 'GET':
        return render_template('activate_api_key.html', username=username)

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
    username, status = verify_session()
    if status != "success":
        return jsonify({"message": status}), 401
    
    return jsonify({"message": "Here are the nodes!",
                    "node_database": db.node_database,
                    }), 200


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
                    "api_key_database": db.convert_sets_to_lists(db._api_key_database),
                    "node_database": db.node_database
                    }), 200


@app.route('/visualize')
def visualize():
    username, status = verify_session()
    if status != "success":
        return jsonify({"message": status}), 401
    
    graph_data = db.convert_to_cytoscape_data(db.node_database)
    return render_template('visualize.html', graph_data=graph_data)

@app.route('/userlist')
def user_list():
    username, status = verify_session()
    if status != "success":
        return jsonify({"message": status}), 401    
    user_data = db.preprocess_user_data(db._user_database)
    return render_template('userlist.html', user_data=user_data)



if __name__ == '__main__':
    ssl_context = {
        'keyfile': 'C:/Certbot/live/ryenandvivekstartup.online/privkey.pem',
        'certfile': 'C:/Certbot/live/ryenandvivekstartup.online/fullchain.pem',
        'cert_reqs': ssl.CERT_OPTIONAL
    }

    # These paths should really be in a .env file that is configured to the host computer
    app.run(ssl_context=('C:/Certbot/live/ryenandvivekstartup.online/fullchain.pem', 
                         'C:/Certbot/live/ryenandvivekstartup.online/privkey.pem'), 
                         host='0.0.0.0', 
                         debug=True, 
                         port=3000)