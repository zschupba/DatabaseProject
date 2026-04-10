-- databaseCRUD.sql
DELIMITER //

-- STUDENT CRUD

CREATE PROCEDURE create_student (
    IN p_student_id         NUMERIC(9,0),
    IN p_first_name         VARCHAR(16),
    IN p_last_name          VARCHAR(16),
    IN p_email              VARCHAR(32),
    IN p_enrollment_date    DATE,
    IN p_enrollment_status  BOOLEAN,
    IN p_dept_id            NUMERIC(6,0)
)
BEGIN
    INSERT INTO student (
        student_id, first_name, last_name, email,
        enrollment_date, enrollment_status, dept_id
    )
    VALUES (
        p_student_id, p_first_name, p_last_name, p_email,
        p_enrollment_date, p_enrollment_status, p_dept_id
    );
END //

CREATE PROCEDURE read_students ()
BEGIN
    SELECT * FROM student;
END //

CREATE PROCEDURE read_student (
    IN p_student_id NUMERIC(9,0)
)
BEGIN
    SELECT s.student_id, s.first_name, s.last_name, s.email,
           s.enrollment_date, s.enrollment_status, d.dept_name
    FROM   student s
    LEFT JOIN department d ON d.dept_id = s.dept_id
    WHERE  s.student_id = p_student_id;
END //

CREATE PROCEDURE update_student (
    IN p_student_id         NUMERIC(9,0),
    IN p_first_name         VARCHAR(16),
    IN p_last_name          VARCHAR(16),
    IN p_email              VARCHAR(32),
    IN p_enrollment_date    DATE,
    IN p_enrollment_status  BOOLEAN,
    IN p_dept_id            NUMERIC(6,0)
)
BEGIN
    UPDATE student
    SET first_name        = p_first_name,
        last_name         = p_last_name,
        email             = p_email,
        enrollment_date   = p_enrollment_date,
        enrollment_status = p_enrollment_status,
        dept_id           = p_dept_id
    WHERE student_id = p_student_id;
END //

CREATE PROCEDURE delete_student (
    IN p_student_id NUMERIC(9,0)
)
BEGIN
    DELETE FROM advisor     WHERE student_id = p_student_id;
    DELETE FROM enrolls     WHERE student_id = p_student_id;
    DELETE FROM useraccount WHERE student_id = p_student_id;
    DELETE FROM student     WHERE student_id = p_student_id;
END //


-- INSTRUCTOR CRUD

CREATE PROCEDURE create_instructor (
    IN p_instructor_id  NUMERIC(8,0),
    IN p_first_name     VARCHAR(16),
    IN p_last_name      VARCHAR(16),
    IN p_salary         NUMERIC(8,2),
    IN p_hire_date      DATE,
    IN p_dept_id        NUMERIC(6,0)
)
BEGIN
    INSERT INTO instructor (
        instructor_id, first_name, last_name, salary, hire_date, dept_id
    )
    VALUES (
        p_instructor_id, p_first_name, p_last_name, p_salary, p_hire_date, p_dept_id
    );
END //

CREATE PROCEDURE read_instructors ()
BEGIN
    SELECT * FROM instructor;
END //

CREATE PROCEDURE read_instructor (
    IN p_instructor_id NUMERIC(8,0)
)
BEGIN
    SELECT i.instructor_id, i.first_name, i.last_name,
           i.salary, i.hire_date, d.dept_name
    FROM   instructor i
    LEFT JOIN department d ON d.dept_id = i.dept_id
    WHERE  i.instructor_id = p_instructor_id;
END //

CREATE PROCEDURE update_instructor (
    IN p_instructor_id  NUMERIC(8,0),
    IN p_first_name     VARCHAR(16),
    IN p_last_name      VARCHAR(16),
    IN p_salary         NUMERIC(8,2),
    IN p_hire_date      DATE,
    IN p_dept_id        NUMERIC(6,0)
)
BEGIN
    UPDATE instructor
    SET first_name = p_first_name,
        last_name  = p_last_name,
        salary     = p_salary,
        hire_date  = p_hire_date,
        dept_id    = p_dept_id
    WHERE instructor_id = p_instructor_id;
END //

CREATE PROCEDURE delete_instructor (
    IN p_instructor_id NUMERIC(8,0)
)
BEGIN
    DELETE FROM advisor     WHERE instructor_id = p_instructor_id;
    DELETE FROM teaches     WHERE instructor_id = p_instructor_id;
    DELETE FROM useraccount WHERE instructor_id = p_instructor_id;
    DELETE FROM instructor  WHERE instructor_id = p_instructor_id;
END //


-- SECTION CRUD

CREATE PROCEDURE create_section (
    IN p_section_id     NUMERIC(6,0),
    IN p_semester       CHAR(6),
    IN p_year           NUMERIC(4,0),
    IN p_capacity       NUMERIC(3,0),
    IN p_course_code    NUMERIC(6,0),
    IN p_classroom_id   NUMERIC(6,0),
    IN p_slot_id        NUMERIC(6,0)
)
BEGIN
    INSERT INTO section (
        section_id, semester, year, capacity, course_code, classroom_id, slot_id
    )
    VALUES (
        p_section_id, p_semester, p_year, p_capacity,
        p_course_code, p_classroom_id, p_slot_id
    );
END //

CREATE PROCEDURE read_sections ()
BEGIN
    SELECT * FROM section;
END //

CREATE PROCEDURE read_section (
    IN p_section_id NUMERIC(6,0)
)
BEGIN
    SELECT se.section_id, se.semester, se.year, se.capacity,
           c.title        AS course_title,
           c.credits,
           b.name         AS building_name,
           cl.room_number,
           t.day_of_week,
           t.start_time,
           t.end_time
    FROM   section   se
    JOIN   course    c  ON c.course_code  = se.course_code
    LEFT JOIN classroom cl ON cl.classroom_id = se.classroom_id
    LEFT JOIN building  b  ON b.building_id   = cl.building_id
    LEFT JOIN timeslot  t  ON t.slot_id        = se.slot_id
    WHERE  se.section_id = p_section_id;
END //

CREATE PROCEDURE update_section (
    IN p_section_id     NUMERIC(6,0),
    IN p_semester       CHAR(6),
    IN p_year           NUMERIC(4,0),
    IN p_capacity       NUMERIC(3,0),
    IN p_course_code    NUMERIC(6,0),
    IN p_classroom_id   NUMERIC(6,0),
    IN p_slot_id        NUMERIC(6,0)
)
BEGIN
    UPDATE section
    SET semester     = p_semester,
        year         = p_year,
        capacity     = p_capacity,
        course_code  = p_course_code,
        classroom_id = p_classroom_id,
        slot_id      = p_slot_id
    WHERE section_id = p_section_id;
END //

CREATE PROCEDURE delete_section (
    IN p_section_id NUMERIC(6,0)
)
BEGIN
    DELETE FROM teaches WHERE section_id = p_section_id;
    DELETE FROM enrolls WHERE section_id = p_section_id;
    DELETE FROM section WHERE section_id = p_section_id;
END //


-- TRANSACTIONS

CREATE PROCEDURE enroll_student (
    IN  p_enrollment_id NUMERIC(6,0),
    IN  p_date_enrolled DATE,
    IN  p_student_id    NUMERIC(9,0),
    IN  p_section_id    NUMERIC(6,0),
    OUT p_result        VARCHAR(128)
)
BEGIN
    DECLARE v_capacity         INT;
    DECLARE v_current_enrolled INT;
    DECLARE v_already_enrolled INT;

    SELECT capacity INTO v_capacity
    FROM   section
    WHERE  section_id = p_section_id;

    IF v_capacity IS NULL THEN
        SET p_result = 'ERROR: Section not found.';
    ELSE
        SELECT COUNT(*) INTO v_already_enrolled
        FROM   enrolls
        WHERE  student_id = p_student_id
          AND  section_id = p_section_id;

        IF v_already_enrolled > 0 THEN
            SET p_result = 'ERROR: Student is already enrolled in this section.';
        ELSE
            SELECT COUNT(*) INTO v_current_enrolled
            FROM   enrolls
            WHERE  section_id = p_section_id;

            IF v_current_enrolled >= v_capacity THEN
                SET p_result = 'ERROR: Section is at full capacity.';
            ELSE
                INSERT INTO enrolls (enrollment_id, grade, date_enrolled, student_id, section_id)
                VALUES (p_enrollment_id, NULL, p_date_enrolled, p_student_id, p_section_id);
                SET p_result = 'SUCCESS: Student enrolled.';
            END IF;
        END IF;
    END IF;
END //


CREATE PROCEDURE assign_instructor_to_class (
    IN  p_teaches_id    NUMERIC(6,0),
    IN  p_instructor_id NUMERIC(8,0),
    IN  p_section_id    NUMERIC(6,0),
    OUT p_result        VARCHAR(128)
)
BEGIN
    DECLARE v_section_exists   INT;
    DECLARE v_already_assigned INT;

    SELECT COUNT(*) INTO v_section_exists
    FROM   section
    WHERE  section_id = p_section_id;

    IF v_section_exists = 0 THEN
        SET p_result = 'ERROR: Section not found.';
    ELSE
        SELECT COUNT(*) INTO v_already_assigned
        FROM   teaches
        WHERE  instructor_id = p_instructor_id
          AND  section_id    = p_section_id;

        IF v_already_assigned > 0 THEN
            SET p_result = 'ERROR: Instructor is already assigned to this section.';
        ELSE
            INSERT INTO teaches (teaches_id, instructor_id, section_id)
            VALUES (p_teaches_id, p_instructor_id, p_section_id);
            SET p_result = 'SUCCESS: Instructor assigned to section.';
        END IF;
    END IF;
END //


CREATE PROCEDURE drop_student_from_section (
    IN  p_enrollment_id NUMERIC(6,0),
    OUT p_result        VARCHAR(128)
)
BEGIN
    DECLARE v_exists INT;

    SELECT COUNT(*) INTO v_exists
    FROM   enrolls
    WHERE  enrollment_id = p_enrollment_id;

    IF v_exists = 0 THEN
        SET p_result = 'ERROR: Enrollment record not found.';
    ELSE
        DELETE FROM enrolls WHERE enrollment_id = p_enrollment_id;
        SET p_result = 'SUCCESS: Student dropped from section.';
    END IF;
END //


CREATE PROCEDURE give_grade (
    IN  p_enrollment_id NUMERIC(6,0),
    IN  p_grade         CHAR(2),
    OUT p_result        VARCHAR(128)
)
BEGIN
    DECLARE v_exists INT;

    IF p_grade NOT IN ('A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D', 'F', 'W') THEN
        SET p_result = 'ERROR: Invalid grade. Must be A, A-, B+, B, B-, C+, C, C-, D, F, or W.';
    ELSE
        SELECT COUNT(*) INTO v_exists
        FROM   enrolls
        WHERE  enrollment_id = p_enrollment_id;

        IF v_exists = 0 THEN
            SET p_result = 'ERROR: Enrollment record not found.';
        ELSE
            UPDATE enrolls
            SET    grade = p_grade
            WHERE  enrollment_id = p_enrollment_id;
            SET p_result = 'SUCCESS: Grade recorded.';
        END IF;
    END IF;
END //

DELIMITER ;