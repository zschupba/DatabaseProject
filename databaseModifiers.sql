-- databaseModifiers.sql
DELIMITER //
-- STUDENT CRUD
CREATE PROCEDURE create_student (
    IN p_student_id NUMERIC(9,0),
    IN p_first_name VARCHAR(16),
    IN p_last_name VARCHAR(16),
    IN p_email VARCHAR(32),
    IN p_enrollment_date DATE,
    IN p_enrollment_status BOOLEAN,
    IN p_dept_id NUMERIC(6,0)
)
BEGIN
    INSERT INTO student (
        student_id,
        first_name,
        last_name,
        email,
        enrollment_date,
        enrollment_status,
        dept_id
    )
    VALUES (
        p_student_id,
        p_first_name,
        p_last_name,
        p_email,
        p_enrollment_date,
        p_enrollment_status,
        p_dept_id
    );
END //

CREATE PROCEDURE read_students ()
BEGIN
    SELECT * FROM student;
END //

CREATE PROCEDURE update_student (
    IN p_student_id NUMERIC(9,0),
    IN p_first_name VARCHAR(16),
    IN p_last_name VARCHAR(16),
    IN p_email VARCHAR(32),
    IN p_enrollment_date DATE,
    IN p_enrollment_status BOOLEAN,
    IN p_dept_id NUMERIC(6,0)
)
BEGIN
    UPDATE student
    SET first_name = p_first_name,
        last_name = p_last_name,
        email = p_email,
        enrollment_date = p_enrollment_date,
        enrollment_status = p_enrollment_status,
        dept_id = p_dept_id
    WHERE student_id = p_student_id;
END //

CREATE PROCEDURE delete_student (
    IN p_student_id NUMERIC(9,0)
)
BEGIN
    DELETE FROM student
    WHERE student_id = p_student_id;
END //


-- INSTRUCTOR CRUD

CREATE PROCEDURE create_instructor (
    IN p_instructor_id NUMERIC(8,0),
    IN p_first_name VARCHAR(16),
    IN p_last_name VARCHAR(16),
    IN p_salary NUMERIC(8,2),
    IN p_hire_date DATE,
    IN p_dept_id NUMERIC(6,0)
)
BEGIN
    INSERT INTO instructor (
        instructor_id,
        first_name,
        last_name,
        salary,
        hire_date,
        dept_id
    )
    VALUES (
        p_instructor_id,
        p_first_name,
        p_last_name,
        p_salary,
        p_hire_date,
        p_dept_id
    );
END //

CREATE PROCEDURE read_instructors ()
BEGIN
    SELECT * FROM instructor;
END //

CREATE PROCEDURE update_instructor (
    IN p_instructor_id NUMERIC(8,0),
    IN p_first_name VARCHAR(16),
    IN p_last_name VARCHAR(16),
    IN p_salary NUMERIC(8,2),
    IN p_hire_date DATE,
    IN p_dept_id NUMERIC(6,0)
)
BEGIN
    UPDATE instructor
    SET first_name = p_first_name,
        last_name = p_last_name,
        salary = p_salary,
        hire_date = p_hire_date,
        dept_id = p_dept_id
    WHERE instructor_id = p_instructor_id;
END //

CREATE PROCEDURE delete_instructor (
    IN p_instructor_id NUMERIC(8,0)
)
BEGIN
    DELETE FROM instructor
    WHERE instructor_id = p_instructor_id;
END //


-- SECTION CRUD

CREATE PROCEDURE create_section (
    IN p_section_id NUMERIC(6,0),
    IN p_semester CHAR(6),
    IN p_year NUMERIC(4,0),
    IN p_capacity NUMERIC(3,0),
    IN p_course_code NUMERIC(6,0),
    IN p_classroom_id NUMERIC(6,0),
    IN p_slot_id NUMERIC(6,0)
)
BEGIN
    INSERT INTO section (
        section_id,
        semester,
        year,
        capacity,
        course_code,
        classroom_id,
        slot_id
    )
    VALUES (
        p_section_id,
        p_semester,
        p_year,
        p_capacity,
        p_course_code,
        p_classroom_id,
        p_slot_id
    );
END //

CREATE PROCEDURE read_sections ()
BEGIN
    SELECT * FROM section;
END //

CREATE PROCEDURE update_section (
    IN p_section_id NUMERIC(6,0),
    IN p_semester CHAR(6),
    IN p_year NUMERIC(4,0),
    IN p_capacity NUMERIC(3,0),
    IN p_course_code NUMERIC(6,0),
    IN p_classroom_id NUMERIC(6,0),
    IN p_slot_id NUMERIC(6,0)
)
BEGIN
    UPDATE section
    SET semester = p_semester,
        year = p_year,
        capacity = p_capacity,
        course_code = p_course_code,
        classroom_id = p_classroom_id,
        slot_id = p_slot_id
    WHERE section_id = p_section_id;
END //

CREATE PROCEDURE delete_section (
    IN p_section_id NUMERIC(6,0)
)
BEGIN
    DELETE FROM section
    WHERE section_id = p_section_id;
END //


-- REQUIRED TRANSACTIONS

CREATE PROCEDURE enroll_student (
    IN p_enrollment_id NUMERIC(6,0),
    IN p_date_enrolled DATE,
    IN p_student_id NUMERIC(9,0),
    IN p_section_id NUMERIC(6,0)
)
BEGIN
    INSERT INTO enrolls (
        enrollment_id,
        grade,
        date_enrolled,
        student_id,
        section_id
    )
    VALUES (
        p_enrollment_id,
        NULL,
        p_date_enrolled,
        p_student_id,
        p_section_id
    );
END //

CREATE PROCEDURE assign_instructor_to_class (
    IN p_teaches_id NUMERIC(6,0),
    IN p_instructor_id NUMERIC(8,0),
    IN p_section_id NUMERIC(6,0)
)
BEGIN
    INSERT INTO teaches (
        teaches_id,
        instructor_id,
        section_id
    )
    VALUES (
        p_teaches_id,
        p_instructor_id,
        p_section_id
    );
END //

CREATE PROCEDURE drop_student_from_section (
    IN p_enrollment_id NUMERIC(6,0)
)
BEGIN
    DELETE FROM enrolls
    WHERE enrollment_id = p_enrollment_id;
END //

CREATE PROCEDURE give_grade (
    IN p_enrollment_id NUMERIC(6,0),
    IN p_grade CHAR(2)
)
BEGIN
    UPDATE enrolls
    SET grade = p_grade
    WHERE enrollment_id = p_enrollment_id;
END //
DELIMITER ;