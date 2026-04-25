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
    return render_template('adminInstructors.html', username=session.get('username'), departments=departments)

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

if __name__ == '__main__':
    app.run(debug=True)