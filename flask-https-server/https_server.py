from flask import Flask, request, jsonify
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
#from base64 import urlsafe_b64encode, urlsafe_b64decode
import os

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
    "user1": (salt1, hash_password("password1", salt1).hex()),
    "user2": (salt2, hash_password("password2", salt2).hex())
}

@app.route('/')
def index():
    return "Hello, this is an https server!"

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')
    
    stored_password_entry = users.get(username, None)

    if stored_password_entry is not None:
        salt = stored_password_entry[0]
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
            # If verification is successful, print the IP and return success message
            client_ip = request.remote_addr
            print(f"Client IP: {client_ip}")
            return jsonify({"message": "Login successful!"}), 200
        except:
            pass

    return jsonify({"message": "Invalid credentials!"}), 401

if __name__ == '__main__':
    app.run(ssl_context=('C:/Certbot/live/ryenandvivekstartup.online/fullchain.pem', 'C:/Certbot/live/ryenandvivekstartup.online/privkey.pem'), host='0.0.0.0', debug=False, port=3000)