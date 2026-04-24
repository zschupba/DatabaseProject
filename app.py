from flask import Flask, render_template, request, jsonify, redirect, url_for, session
import mysql.connector
from mysql.connector import Error
import hashlib
 
app = Flask(__name__)
app.secret_key = 'ksu_secret_key_2025'
 
# --- Database Configuration ---
dbConfig = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'ksu'
}
 
def getDbConnection():
    try:
        conn = mysql.connector.connect(**dbConfig)
        return conn
    except Error as e:
        print(f"Database connection error: {e}")
        return None
 
def login_required(role=None):
    def decorator(f):
        def wrapper(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('login'))
            if role and session.get('role') != role:
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator
 
def dashboard():
    role = session.get('role')
    if role == 'admin':
        return redirect(url_for('admin_home'))
    elif role == 'instructor':
        return redirect(url_for('instructor_home'))
    elif role == 'student':
        return redirect(url_for('student_home'))
    return redirect(url_for('login'))
 
#############  AUTH   ######################
 
@app.route('/')
def index():
    if 'user_id' in session:
        return dashboard()
    return redirect(url_for('login'))
 
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
 
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '').strip()
 
    if not username or not password:
        return jsonify({'error': 'Username and password are required.'}), 400
 
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'Database connection failed.'}), 500
 
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            'SELECT * FROM useraccount WHERE username = %s AND password = %s',
            (username, password)
        )
        user = cursor.fetchone()
        cursor.close()
        conn.close()
 
        if not user:
            return jsonify({'error': 'Invalid username or password.'}), 401
 
        session['user_id']       = int(user['user_id'])
        session['username']      = user['username']
        session['role']          = user['role']
        session['student_id']    = user.get('student_id')
        session['instructor_id'] = user.get('instructor_id')
 
        role = user['role']
        if role == 'admin':
            return jsonify({'redirect': url_for('admin_home')})
        elif role == 'instructor':
            return jsonify({'redirect': url_for('instructor_home')})
        else:
            return jsonify({'redirect': url_for('student_home')})
    except Error as e:
        return jsonify({'error': str(e)}), 500
 
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))