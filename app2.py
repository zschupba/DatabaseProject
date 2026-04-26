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

    try:
        data = request.get_json()

        if not data:
            return jsonify({'error': 'Invalid request format'}), 400

        username = data.get('username', '').strip()
        password = data.get('password', '').strip()

        if not username or not password:
            return jsonify({'error': 'Username and password are required.'}), 400

        conn = getDbConnection()
        if not conn:
            return jsonify({'error': 'Database connection failed.'}), 500

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

        session['user_id'] = int(user['user_id'])
        session['username'] = user['username']
        session['role'] = user['role']

        if user['role'] == 'admin':
            return jsonify({'redirect': url_for('admin_home')})
        elif user['role'] == 'instructor':
            return jsonify({'redirect': url_for('instructor_home')})
        else:
            return jsonify({'redirect': url_for('student_home')})

    except Exception as e:
        print("ERROR:", e)  
        return jsonify({'error': 'Server error'}), 500
 
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/admin')
def admin_home():
    return render_template("admin.html")

@app.route('/instructor')
def instructor_home():
    return "Instructor Page"

@app.route('/student')
def student_home():
    return "Student Page"

@app.route('/view-students')
def view_students():
    conn = getDbConnection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM student")
    students = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("students.html", students=students)

@app.route('/add-student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'GET':
        return render_template('add_student.html')

    # POST (form submit)
    student_id = request.form.get('student_id')
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')

    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO student (student_id, first_name, last_name, email)
        VALUES (%s, %s, %s, %s)
    """, (student_id, first_name, last_name, email))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/view-students')

@app.route('/delete-student/<int:student_id>')
def delete_student(student_id):
    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM student WHERE student_id = %s", (student_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/view-students')

@app.route('/edit-student/<int:student_id>', methods=['GET', 'POST'])
def edit_student(student_id):
    conn = getDbConnection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM student WHERE student_id = %s", (student_id,))
        student = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template("edit_student.html", student=student)

    # POST (update)
    first_name = request.form.get('first_name')
    last_name = request.form.get('last_name')
    email = request.form.get('email')

    cursor.execute("""
        UPDATE student
        SET first_name=%s, last_name=%s, email=%s
        WHERE student_id=%s
    """, (first_name, last_name, email, student_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/view-students')


@app.route('/view-courses')
def view_courses():
    conn = getDbConnection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM course")
    courses = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("courses.html", courses=courses)

@app.route('/add-course', methods=['GET', 'POST'])
def add_course():
    if request.method == 'GET':
        return render_template('add_course.html')

    course_code = request.form.get('course_code')
    title = request.form.get('title')
    credits = request.form.get('credits')

    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO course (course_code, title, credits)
        VALUES (%s, %s, %s)
    """, (course_code, title, credits))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/view-courses')

@app.route('/delete-course/<int:course_code>')
def delete_course(course_code):
    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM course WHERE course_code = %s", (course_code,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/view-courses')

@app.route('/edit-course/<int:course_code>', methods=['GET', 'POST'])
def edit_course(course_code):
    conn = getDbConnection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM course WHERE course_code = %s", (course_code,))
        course = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template("edit_course.html", course=course)

    title = request.form.get('title')
    credits = request.form.get('credits')

    cursor.execute("""
        UPDATE course
        SET title=%s, credits=%s
        WHERE course_code=%s
    """, (title, credits, course_code))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/view-courses')

@app.route('/view-sections')
def view_sections():
    conn = getDbConnection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM section")
    sections = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("sections.html", sections=sections)


@app.route('/add-section', methods=['GET', 'POST'])
def add_section():
    if request.method == 'GET':
        return render_template('add_section.html')

    try:
        section_id = request.form.get('section_id')
        semester = request.form.get('semester')
        year = request.form.get('year')
        capacity = request.form.get('capacity')
        course_code = request.form.get('course_code')

        print(section_id, semester, year, capacity, course_code)  # 👈 DEBUG

        conn = getDbConnection()
        cursor = conn.cursor()

        cursor.execute("""
    INSERT INTO section (
        section_id, semester, year, capacity,
        course_code, classroom_id, slot_id
    )
    VALUES (%s, %s, %s, %s, %s, NULL, NULL)
""", (section_id, semester, year, capacity, course_code))

        conn.commit()
        cursor.close()
        conn.close()

        return redirect('/view-sections')

    except Exception as e:
        print("ERROR:", e)   # 👈 THIS WILL SHOW REAL ISSUE
        return "Error occurred"
    

@app.route('/delete-section/<int:section_id>')
def delete_section(section_id):
    conn = getDbConnection()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM section WHERE section_id = %s", (section_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/view-sections')   

@app.route('/edit-section/<int:section_id>', methods=['GET', 'POST'])
def edit_section(section_id):
    conn = getDbConnection()
    cursor = conn.cursor(dictionary=True)

    if request.method == 'GET':
        cursor.execute("SELECT * FROM section WHERE section_id = %s", (section_id,))
        section = cursor.fetchone()
        cursor.close()
        conn.close()
        return render_template("edit_section.html", section=section)

    semester = request.form.get('semester')
    year = request.form.get('year')
    capacity = request.form.get('capacity')

    cursor.execute("""
        UPDATE section
        SET semester=%s, year=%s, capacity=%s
        WHERE section_id=%s
    """, (semester, year, capacity, section_id))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect('/view-sections')

    
if __name__ == "__main__":
     app.run(debug=True)
