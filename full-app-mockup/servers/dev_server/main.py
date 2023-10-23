from flask import Flask, request, jsonify, render_template, redirect, url_for, session
import requests
import json
import time
from core.database import CreateDatabaseInterface
from core.server import AuthenticationManager
import ssl

db = CreateDatabaseInterface('mongodb', {'host': '127.0.0.1', 'port': 27017, 'database_name': 'test'})
db.add_user('ryen', 'T5TCoAXS3Ng0Fr3')
db.add_user('vivek', 'jr5dXC3mS799sGq')

auth = AuthenticationManager(database=db)

app = Flask(__name__)
# secret key
app.secret_key = 'asdfasdf'

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', None)
        password = request.form.get('password', None)
        if auth.login_user(username, password):
            return redirect(url_for('home'))
        else:
            return jsonify({'error': 'Invalid username or password'}), 401
    else:
        return render_template('login.html', error="Invalid username or password")

@app.route('/logout', methods=['GET'])
def logout():
    auth.logout_user(session['username'], session['session_id'])
    session['authenticated'] = False
    session['username'] = None
    session['session_id'] = None
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
@auth.login_session_required
def home():
    return render_template('home.html', username=session.get('username', None))

@app.route('/get_active_nodes', methods=['GET'])
@auth.login_session_required
def get_active_nodes():
    result = requests.get('http://127.0.0.1:5000/list_nodes')
    return jsonify(result.json())

@app.route('/make_node', methods=['POST'])
@auth.login_session_required
def make_node():
    node_name = request.json.get('node_name')
    node_ip = '127.0.0.1'
    node_port = int(request.json.get('node_port')) + 9000
    
    if not node_name or not node_ip or not node_port:
        return jsonify({"error": "Insufficient node info!"}), 400
    data = {
        'node_name': node_name,
        'node_ip': node_ip,
        'node_port': node_port
    }
    result = requests.post('http://127.0.0.1:5000/make_node', json=data)
    return jsonify(result.json()), result.status_code

@app.route('/delete_node', methods=['POST'])
@auth.login_session_required
def delete_node():
    node_name = request.json.get('node_name')
    if not node_name:
        return jsonify({"error": "Node name is required!"}), 400
    data = {
        'node_name': node_name,
    }

    result = requests.post('http://127.0.0.1:5000/delete_node', json=data)
    return jsonify(result.json()), result.status_code

if __name__ == '__main__':
    context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2) #Change to v1_3 when available
    context.load_cert_chain(certfile='C:/Certbot/live/ryenandvivekstartup.online/fullchain.pem', 
                            keyfile='C:/Certbot/live/ryenandvivekstartup.online/privkey.pem')
    #context.verify_mode = ssl.CERT_OPTIONAL

    app.run(ssl_context=context, host='0.0.0.0', debug=False, port=3000)