from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
#from base64 import urlsafe_b64encode, urlsafe_b64decode
import os
import time

app = Flask(__name__)


def hash_password(password, salt):
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    return kdf.derive(password.encode())

def generate_salt(length=32):
    return os.urandom(length)

# Simple hardcoded "database" for demonstration
# Passwords are pre-hashed for demonstration purposes
salt1 = generate_salt()
salt2 = generate_salt()
users = {
    "user1": (salt1.hex(), hash_password("password1", salt1).hex()),
    "user2": (salt2.hex(), hash_password("password2", salt2).hex())
}

session_keys = {}

api_keys = {}



@app.route('/')
def index():
    return "Hello, this is an https server!"

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    stored_password_entry = users.get(username, None)

    if stored_password_entry is not None:
        salt = bytes.fromhex(stored_password_entry[0])
        stored_password_hash = stored_password_entry[1]
        try:
            # Compare the given password with the stored hashed password
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
                backend=default_backend()
            )
            kdf.verify(password.encode(), bytes.fromhex(stored_password_hash))

            # Generate a session key
            client_ip = request.remote_addr
            session_key = generate_salt().hex()
            # Store the session key in the server's database along with client id and timestamp plus six hours
            session_keys[session_key] = (username, client_ip, time.time() + 21600)
            
            print(f"Client IP: {client_ip}")
            return jsonify({"message": "Login successful!", "session_key":session_key}), 200
        except:
            pass

    return jsonify({"message": "Invalid credentials!"}), 401


@app.route('/home', methods=['POST'])
def home():
    session_key = request.json.get('session_key')
    client_ip = request.remote_addr
    if session_key in session_keys:
        if session_keys[session_key][1] == client_ip:
            # Check if session key has expired
            if session_keys[session_key][2] > time.time():
                # Return the data requested by the client
                username = session_keys[session_key][0]
                return jsonify({"message": f"API access for {username} successful!"}), 200
            else:
                # Session key has expired
                del session_keys[session_key]
                return jsonify({"message": "Session key has expired!"}), 401
        else:
            return jsonify({"message": "Client IP does not match original session!"}), 401
    else:
        # Session key not found
        return jsonify({"message": "Session key not found!"}), 401



if __name__ == '__main__':
    # These paths should really be in a .env file that is configured to the host computer
    app.run(ssl_context=('C:/Certbot/live/ryenandvivekstartup.online/fullchain.pem', 'C:/Certbot/live/ryenandvivekstartup.online/privkey.pem'), host='0.0.0.0', debug=False, port=3000)