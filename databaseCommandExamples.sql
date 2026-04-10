--  STUDENT CRUD

CALL create_student(100000011, 'Joe', 'Turner', 'jturner@kent.edu', '2025-08-20', TRUE, 10, 9000000015, 'jturner', 'pass1234');
CALL read_student(100000011);
CALL update_student(100000011, 'Joe', 'Turner', 'jturner2@kent.edu', '2025-08-20', TRUE, 20);
CALL delete_student(100000011);



--  INSTRUCTOR CRUD

-- Create a new instructor
CALL create_instructor(1004, 'David', 'Huge', 95000.00, '2024-01-15', 10, 9000000016, 'dhuge', 'pass1234');
CALL read_instructor(1004);
CALL update_instructor(1004, 'David', 'Huge', 98000.00, '2024-01-15', 20);
CALL delete_instructor(1004);



--  SECTION CRUD

CALL create_section(1005, 'Spring', 2025, 30, 401, 203, 3);
CALL read_sections();
CALL read_section(1005);
CALL update_section(1005, 'Spring', 2025, 30, 401, 204, 5);
CALL delete_section(1005);



--  TRANSACTIONS

CALL enroll_student(11, CURDATE(), 100000003, 1001, @result);
SELECT @result;
-- should error
CALL enroll_student(12, CURDATE(), 100000003, 1001, @result);
SELECT @result;
-- should error
CALL enroll_student(12, CURDATE(), 100000003, 9999, @result);
SELECT @result;

CALL assign_instructor_to_class(6, 1002, 1001, @result);
SELECT @result;

CALL drop_student_from_section(11, @result);
SELECT @result;

-- should error
CALL drop_student_from_section(999, @result);
SELECT @result;

CALL give_grade(1, 'A', @result);
SELECT @result;
-- should error
CALL give_grade(1, 'Z', @result);
SELECT @result;
-- should error
CALL give_grade(999, 'B+', @result);
SELECT @result;


-- User accounts
CALL create_user_admin(9000000017, 'sysadmin', 'adminpass');
CALL read_user(9000000015);
CALL update_user_password(9000000015, 'newpass5678');
CALL delete_user(9000000015);