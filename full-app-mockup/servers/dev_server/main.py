from flask import Flask, request, jsonify, render_template, redirect, url_for, session

from core.database import CreateDatabaseInterface
from core.server import AuthenticationManager

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


if __name__ == '__main__':
    app.run(port=5002, debug=True)