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

# ── AUTH ──────────────────────────────────────────────────────

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

# ── ADMIN ROUTES ──────────────────────────────────────────────

@app.route('/admin')
def admin_home():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    return render_template('admin.html', username=session.get('username'))

@app.route('/admin/students')
def admin_students():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = getDbConnection()
    departments = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT dept_id, dept_name FROM department ORDER BY dept_name')
        departments = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('adminStudents.html', username=session.get('username'), departments=departments)

@app.route('/admin/instructors')
def admin_instructors():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = getDbConnection()
    departments = []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT dept_id, dept_name FROM department ORDER BY dept_name')
        departments = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('adminInstructor.html', username=session.get('username'), departments=departments)

@app.route('/admin/sections')
def admin_sections():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = getDbConnection()
    courses, classrooms, timeslots = [], [], []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT course_code, title FROM course ORDER BY title')
        courses = cursor.fetchall()
        cursor.execute('SELECT cl.classroom_id, b.name AS building, cl.room_number FROM classroom cl JOIN building b ON b.building_id = cl.building_id ORDER BY b.name, cl.room_number')
        classrooms = cursor.fetchall()
        cursor.execute('SELECT slot_id, day_of_week, start_time, end_time FROM timeslot ORDER BY day_of_week, start_time')
        timeslots = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('adminSections.html', username=session.get('username'), courses=courses, classrooms=classrooms, timeslots=timeslots)

# ── INSTRUCTOR ROUTES ─────────────────────────────────────────

@app.route('/instructor')
def instructor_home():
    if session.get('role') != 'instructor':
        return redirect(url_for('login'))
    return render_template('instructor.html', username=session.get('username'), instructor_id=session.get('instructor_id'))

# ── STUDENT ROUTES ────────────────────────────────────────────

@app.route('/student')
def student_home():
    if session.get('role') != 'student':
        return redirect(url_for('login'))
    return render_template('student.html', username=session.get('username'), student_id=session.get('student_id'))

# ── ADMIN API ─────────────────────────────────────────────────

@app.route('/api/admin/students', methods=['GET'])
def api_get_students():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('read_students')
        rows = []
        for r in cursor.stored_results():
            rows = r.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'students': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students', methods=['POST'])
def api_create_student():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('create_student', [
            data['student_id'], data['first_name'], data['last_name'],
            data['email'], data['enrollment_date'], True, data['dept_id'],
            data['user_id'], data['username'], data['password']
        ])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students/<int:student_id>', methods=['PUT'])
def api_update_student(student_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('update_student', [
            student_id, data['first_name'], data['last_name'],
            data['email'], data['enrollment_date'], data['enrollment_status'], data['dept_id']
        ])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/students/<int:student_id>', methods=['DELETE'])
def api_delete_student(student_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('delete_student', [student_id])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/instructors', methods=['GET'])
def api_get_instructors():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('read_instructors')
        rows = []
        for r in cursor.stored_results():
            rows = r.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'instructors': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/instructors', methods=['POST'])
def api_create_instructor():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('create_instructor', [
            data['instructor_id'], data['first_name'], data['last_name'],
            data['salary'], data['hire_date'], data['dept_id'],
            data['user_id'], data['username'], data['password']
        ])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/instructors/<int:instructor_id>', methods=['PUT'])
def api_update_instructor(instructor_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('update_instructor', [
            instructor_id, data['first_name'], data['last_name'],
            data['salary'], data['hire_date'], data['dept_id']
        ])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/instructors/<int:instructor_id>', methods=['DELETE'])
def api_delete_instructor(instructor_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('delete_instructor', [instructor_id])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/sections', methods=['GET'])
def api_get_sections():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('read_sections')
        rows = []
        for r in cursor.stored_results():
            rows = r.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'sections': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/sections', methods=['POST'])
def api_create_section():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('create_section', [
            data['section_id'], data['semester'], data['year'],
            data['capacity'], data['course_code'], data['classroom_id'], data['slot_id']
        ])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/sections/<int:section_id>', methods=['PUT'])
def api_update_section(section_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('update_section', [
            section_id, data['semester'], data['year'],
            data['capacity'], data['course_code'], data['classroom_id'], data['slot_id']
        ])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/sections/<int:section_id>', methods=['DELETE'])
def api_delete_section(section_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.callproc('delete_section', [section_id])
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/assign_instructor', methods=['POST'])
def api_assign_instructor():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        args = [data['teaches_id'], data['instructor_id'], data['section_id'], '']
        cursor.callproc('assign_instructor_to_class', args)
        conn.commit()
        result_msg = args[3]
        cursor.close()
        conn.close()
        if 'ERROR' in str(result_msg):
            return jsonify({'error': result_msg}), 400
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

# ── INSTRUCTOR API ────────────────────────────────────────────

@app.route('/api/instructor/sections', methods=['GET'])
def api_instructor_sections():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    instructor_id = session.get('instructor_id')
    semester = request.args.get('semester', 'Spring')
    year = request.args.get('year', '2025')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT se.section_id, c.title AS course_title, se.semester, se.year, se.capacity,
                   COUNT(e.enrollment_id) AS enrolled
            FROM teaches te
            JOIN section se ON se.section_id = te.section_id
            JOIN course c ON c.course_code = se.course_code
            LEFT JOIN enrolls e ON e.section_id = se.section_id
            WHERE te.instructor_id = %s AND se.semester = %s AND se.year = %s
            GROUP BY se.section_id, c.title, se.semester, se.year, se.capacity
        ''', (instructor_id, semester, year))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'sections': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/roster/<int:section_id>', methods=['GET'])
def api_instructor_roster(section_id):
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.callproc('instructor_section_roster', [section_id])
        rows = []
        for r in cursor.stored_results():
            rows = r.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'roster': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/grade', methods=['POST'])
def api_give_grade():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        args = [data['enrollment_id'], data['grade'], '']
        cursor.callproc('give_grade', args)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/drop_student', methods=['POST'])
def api_instructor_drop_student():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        args = [data['enrollment_id'], '']
        cursor.callproc('drop_student_from_section', args)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/update_self', methods=['POST'])
def api_instructor_update_self():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    instructor_id = session.get('instructor_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE instructor SET first_name=%s, last_name=%s WHERE instructor_id=%s',
            (data['first_name'], data['last_name'], instructor_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

# ── STUDENT API ───────────────────────────────────────────────

@app.route('/api/student/sections', methods=['GET'])
def api_available_sections():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    semester = request.args.get('semester', 'Spring')
    year = request.args.get('year', '2025')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT se.section_id, c.title AS course_title, c.credits, se.semester, se.year,
                   se.capacity, COUNT(e.enrollment_id) AS enrolled,
                   t.day_of_week, t.start_time, t.end_time,
                   b.name AS building_name, cl.room_number
            FROM section se
            JOIN course c ON c.course_code = se.course_code
            LEFT JOIN enrolls e ON e.section_id = se.section_id
            LEFT JOIN timeslot t ON t.slot_id = se.slot_id
            LEFT JOIN classroom cl ON cl.classroom_id = se.classroom_id
            LEFT JOIN building b ON b.building_id = cl.building_id
            WHERE se.semester = %s AND se.year = %s
            GROUP BY se.section_id, c.title, c.credits, se.semester, se.year,
                     se.capacity, t.day_of_week, t.start_time, t.end_time, b.name, cl.room_number
        ''', (semester, year))
        rows = cursor.fetchall()
        # convert timedelta to string
        for row in rows:
            if row.get('start_time') is not None:
                row['start_time'] = str(row['start_time'])
            if row.get('end_time') is not None:
                row['end_time'] = str(row['end_time'])
        cursor.close()
        conn.close()
        return jsonify({'sections': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/enroll', methods=['POST'])
def api_student_enroll():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    student_id = session.get('student_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT MAX(enrollment_id) AS max_id FROM enrolls')
        row = cursor.fetchone()
        new_id = (row['max_id'] or 0) + 1

        args = [new_id, data['date_enrolled'], student_id, data['section_id'], '']
        cursor.callproc('enroll_student', args)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/drop', methods=['POST'])
def api_student_drop():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        args = [data['enrollment_id'], '']
        cursor.callproc('drop_student_from_section', args)
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/my_sections', methods=['GET'])
def api_student_my_sections():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    student_id = session.get('student_id')
    semester = request.args.get('semester', '')
    year = request.args.get('year', '')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        query = '''
            SELECT e.enrollment_id, e.grade, e.date_enrolled,
                   se.section_id, se.semester, se.year,
                   c.title AS course_title, c.credits,
                   t.day_of_week, t.start_time, t.end_time,
                   b.name AS building_name, cl.room_number
            FROM enrolls e
            JOIN section se ON se.section_id = e.section_id
            JOIN course c ON c.course_code = se.course_code
            LEFT JOIN timeslot t ON t.slot_id = se.slot_id
            LEFT JOIN classroom cl ON cl.classroom_id = se.classroom_id
            LEFT JOIN building b ON b.building_id = cl.building_id
            WHERE e.student_id = %s
        '''
        params = [student_id]
        if semester:
            query += ' AND se.semester = %s'
            params.append(semester)
        if year:
            query += ' AND se.year = %s'
            params.append(year)
        query += ' ORDER BY se.year DESC, se.semester, c.title'
        cursor.execute(query, params)
        rows = cursor.fetchall()
        for row in rows:
            if row.get('start_time') is not None:
                row['start_time'] = str(row['start_time'])
            if row.get('end_time') is not None:
                row['end_time'] = str(row['end_time'])
        cursor.close()
        conn.close()
        return jsonify({'sections': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/advisor', methods=['GET'])
def api_student_advisor():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    student_id = session.get('student_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT i.first_name, i.last_name, d.dept_name, a.start_date
            FROM advisor a
            JOIN instructor i ON i.instructor_id = a.instructor_id
            LEFT JOIN department d ON d.dept_id = i.dept_id
            WHERE a.student_id = %s
        ''', (student_id,))
        advisor = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({'advisor': advisor})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/update_self', methods=['POST'])
def api_student_update_self():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    student_id = session.get('student_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE student SET first_name=%s, last_name=%s, email=%s WHERE student_id=%s',
            (data['first_name'], data['last_name'], data['email'], student_id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/student/info', methods=['GET'])
def api_student_info():
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    student_id = session.get('student_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT s.student_id, s.first_name, s.last_name, s.email,
                   s.enrollment_date, s.enrollment_status, d.dept_name
            FROM student s LEFT JOIN department d ON d.dept_id = s.dept_id
            WHERE s.student_id = %s
        ''', (student_id,))
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({'info': info})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/info', methods=['GET'])
def api_instructor_info():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    instructor_id = session.get('instructor_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT i.instructor_id, i.first_name, i.last_name, i.hire_date, d.dept_name
            FROM instructor i LEFT JOIN department d ON d.dept_id = i.dept_id
            WHERE i.instructor_id = %s
        ''', (instructor_id,))
        info = cursor.fetchone()
        cursor.close()
        conn.close()
        return jsonify({'info': info})
    except Error as e:
        return jsonify({'error': str(e)}), 500


# ── ADMIN ROUTES (new pages) ──────────────────────────────────

@app.route('/admin/extras')
def admin_extras():
    if session.get('role') != 'admin':
        return redirect(url_for('login'))
    conn = getDbConnection()
    departments, buildings = [], []
    if conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT dept_id, dept_name FROM department ORDER BY dept_name')
        departments = cursor.fetchall()
        cursor.execute('SELECT building_id, name FROM building ORDER BY name')
        buildings = cursor.fetchall()
        cursor.close()
        conn.close()
    return render_template('adminExtras.html', username=session.get('username'), departments=departments, buildings=buildings)

# ── ADMIN API (courses) ───────────────────────────────────────

@app.route('/api/admin/courses', methods=['GET'])
def api_get_courses():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT c.course_code, c.title, c.credits, d.dept_name FROM course c LEFT JOIN department d ON d.dept_id = c.dept_id ORDER BY c.title')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'courses': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/courses', methods=['POST'])
def api_create_course():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO course (course_code, title, credits, dept_id) VALUES (%s, %s, %s, %s)',
            (data['course_code'], data['title'], data['credits'], data['dept_id']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/courses/<int:course_code>', methods=['PUT'])
def api_update_course(course_code):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE course SET title=%s, credits=%s, dept_id=%s WHERE course_code=%s',
            (data['title'], data['credits'], data['dept_id'], course_code))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/courses/<int:course_code>', methods=['DELETE'])
def api_delete_course(course_code):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prereq WHERE course_code=%s OR prereq_course_id=%s', (course_code, course_code))
        cursor.execute('DELETE FROM section WHERE course_code=%s', (course_code,))
        cursor.execute('DELETE FROM course WHERE course_code=%s', (course_code,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

# ── ADMIN API (classrooms) ────────────────────────────────────

@app.route('/api/admin/classrooms', methods=['GET'])
def api_get_classrooms():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT cl.classroom_id, b.name AS building_name, cl.room_number, cl.capacity FROM classroom cl JOIN building b ON b.building_id = cl.building_id ORDER BY b.name, cl.room_number')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'classrooms': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classrooms', methods=['POST'])
def api_create_classroom():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO classroom (classroom_id, building_id, room_number, capacity) VALUES (%s, %s, %s, %s)',
            (data['classroom_id'], data['building_id'], data['room_number'], data['capacity']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classrooms/<int:classroom_id>', methods=['PUT'])
def api_update_classroom(classroom_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE classroom SET building_id=%s, room_number=%s, capacity=%s WHERE classroom_id=%s',
            (data['building_id'], data['room_number'], data['capacity'], classroom_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/classrooms/<int:classroom_id>', methods=['DELETE'])
def api_delete_classroom(classroom_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE section SET classroom_id=NULL WHERE classroom_id=%s', (classroom_id,))
        cursor.execute('DELETE FROM classroom WHERE classroom_id=%s', (classroom_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

# ── ADMIN API (departments) ───────────────────────────────────

@app.route('/api/admin/departments', methods=['GET'])
def api_get_departments():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT d.dept_id, d.dept_name, b.name AS building_name, d.budget FROM department d LEFT JOIN building b ON b.building_id = d.office_building ORDER BY d.dept_name')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'departments': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/departments', methods=['POST'])
def api_create_department():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO department (dept_id, dept_name, office_building, budget) VALUES (%s, %s, %s, %s)',
            (data['dept_id'], data['dept_name'], data['office_building'] or None, data['budget'] or None))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/departments/<int:dept_id>', methods=['PUT'])
def api_update_department(dept_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE department SET dept_name=%s, office_building=%s, budget=%s WHERE dept_id=%s',
            (data['dept_name'], data['office_building'] or None, data['budget'] or None, dept_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/departments/<int:dept_id>', methods=['DELETE'])
def api_delete_department(dept_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE student SET dept_id=NULL WHERE dept_id=%s', (dept_id,))
        cursor.execute('UPDATE instructor SET dept_id=NULL WHERE dept_id=%s', (dept_id,))
        cursor.execute('UPDATE course SET dept_id=NULL WHERE dept_id=%s', (dept_id,))
        cursor.execute('DELETE FROM department WHERE dept_id=%s', (dept_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

# ── ADMIN API (timeslots) ─────────────────────────────────────

@app.route('/api/admin/timeslots', methods=['GET'])
def api_get_timeslots():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT slot_id, day_of_week, start_time, end_time FROM timeslot ORDER BY day_of_week, start_time')
        rows = cursor.fetchall()
        for row in rows:
            row['start_time'] = str(row['start_time'])
            row['end_time'] = str(row['end_time'])
        cursor.close()
        conn.close()
        return jsonify({'timeslots': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/timeslots', methods=['POST'])
def api_create_timeslot():
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO timeslot (slot_id, day_of_week, start_time, end_time) VALUES (%s, %s, %s, %s)',
            (data['slot_id'], data['day_of_week'], data['start_time'], data['end_time']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/timeslots/<int:slot_id>', methods=['PUT'])
def api_update_timeslot(slot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE timeslot SET day_of_week=%s, start_time=%s, end_time=%s WHERE slot_id=%s',
            (data['day_of_week'], data['start_time'], data['end_time'], slot_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/admin/timeslots/<int:slot_id>', methods=['DELETE'])
def api_delete_timeslot(slot_id):
    if session.get('role') != 'admin':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('UPDATE section SET slot_id=NULL WHERE slot_id=%s', (slot_id,))
        cursor.execute('DELETE FROM timeslot WHERE slot_id=%s', (slot_id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

# ── INSTRUCTOR API (advisor + prereqs) ───────────────────────

@app.route('/api/instructor/add_advisor', methods=['POST'])
def api_add_advisor():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    instructor_id = session.get('instructor_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT MAX(advisor_id) AS max_id FROM advisor')
        row = cursor.fetchone()
        new_id = (row['max_id'] or 0) + 1
        cursor.execute('INSERT INTO advisor (advisor_id, start_date, student_id, instructor_id) VALUES (%s, CURDATE(), %s, %s)',
            (new_id, data['student_id'], instructor_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/remove_advisor', methods=['POST'])
def api_remove_advisor():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    instructor_id = session.get('instructor_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM advisor WHERE student_id=%s AND instructor_id=%s',
            (data['student_id'], instructor_id))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/my_advisees', methods=['GET'])
def api_my_advisees():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    instructor_id = session.get('instructor_id')
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT s.student_id, s.first_name, s.last_name, s.email, a.start_date
            FROM advisor a JOIN student s ON s.student_id = a.student_id
            WHERE a.instructor_id = %s ORDER BY s.last_name
        ''', (instructor_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'advisees': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/prereqs/<int:course_code>', methods=['GET'])
def api_get_prereqs(course_code):
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT p.prereq_course_id, c.title, p.req_type
            FROM prereq p JOIN course c ON c.course_code = p.prereq_course_id
            WHERE p.course_code = %s
        ''', (course_code,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'prereqs': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/prereqs', methods=['POST'])
def api_add_prereq():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO prereq (course_code, prereq_course_id, req_type) VALUES (%s, %s, %s)',
            (data['course_code'], data['prereq_course_id'], data['req_type']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/prereqs', methods=['DELETE'])
def api_remove_prereq():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    data = request.get_json()
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor()
        cursor.execute('DELETE FROM prereq WHERE course_code=%s AND prereq_course_id=%s',
            (data['course_code'], data['prereq_course_id']))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'success': True})
    except Error as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/instructor/courses', methods=['GET'])
def api_instructor_courses():
    if session.get('role') != 'instructor':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT course_code, title FROM course ORDER BY title')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        return jsonify({'courses': rows})
    except Error as e:
        return jsonify({'error': str(e)}), 500

# ── STUDENT API (section info) ────────────────────────────────

@app.route('/api/student/section_info/<int:section_id>', methods=['GET'])
def api_section_info(section_id):
    if session.get('role') != 'student':
        return jsonify({'error': 'Unauthorized'}), 403
    conn = getDbConnection()
    if not conn:
        return jsonify({'error': 'DB error'}), 500
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute('''
            SELECT se.section_id, se.semester, se.year, se.capacity,
                   c.title AS course_title, c.credits,
                   COUNT(e.enrollment_id) AS enrolled,
                   t.day_of_week, t.start_time, t.end_time,
                   b.name AS building_name, cl.room_number,
                   i.first_name AS instructor_first, i.last_name AS instructor_last
            FROM section se
            JOIN course c ON c.course_code = se.course_code
            LEFT JOIN enrolls e ON e.section_id = se.section_id
            LEFT JOIN timeslot t ON t.slot_id = se.slot_id
            LEFT JOIN classroom cl ON cl.classroom_id = se.classroom_id
            LEFT JOIN building b ON b.building_id = cl.building_id
            LEFT JOIN teaches te ON te.section_id = se.section_id
            LEFT JOIN instructor i ON i.instructor_id = te.instructor_id
            WHERE se.section_id = %s
            GROUP BY se.section_id, se.semester, se.year, se.capacity,
                     c.title, c.credits, t.day_of_week, t.start_time, t.end_time,
                     b.name, cl.room_number, i.first_name, i.last_name
        ''', (section_id,))
        info = cursor.fetchone()
        if info:
            if info.get('start_time') is not None:
                info['start_time'] = str(info['start_time'])
            if info.get('end_time') is not None:
                info['end_time'] = str(info['end_time'])
        cursor.close()
        conn.close()
        return jsonify({'info': info})
    except Error as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)