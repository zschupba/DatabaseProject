--  STUDENT CRUD


-- Create a new student
CALL create_student(100000011, 'Joe', 'Turner', 'jturner@kent.edu', '2025-08-20', TRUE, 10);

-- Read all students
CALL read_students();

-- Read one student
CALL read_student(100000011);

-- Update a student
CALL update_student(100000011, 'Joe', 'Turner', 'jturner2@kent.edu', '2025-08-20', TRUE, 20);

-- Delete a student
CALL delete_student(100000011);



--  INSTRUCTOR CRUD

-- Create a new instructor
CALL create_instructor(1004, 'David', 'Huge', 95000.00, '2024-01-15', 10);

-- Read all instructors
CALL read_instructors();

-- Read one instructor
CALL read_instructor(1004);

-- Update an instructor
CALL update_instructor(1004, 'David', 'Huge', 98000.00, '2024-01-15', 20);

-- Delete an instructor
CALL delete_instructor(1004);



--  SECTION CRUD

-- Create a new section
CALL create_section(1005, 'Spring', 2025, 30, 401, 203, 3);

-- Read all sections
CALL read_sections();

-- Read one section
CALL read_section(1005);

-- Update a section (change classroom and timeslot)
CALL update_section(1005, 'Spring', 2025, 30, 401, 204, 5);

-- Delete a section
CALL delete_section(1005);



--  TRANSACTIONS

-- Enroll a student into a section
CALL enroll_student(11, CURDATE(), 100000003, 1001, @result);
SELECT @result;

-- Try enrolling the same student again (should error)
CALL enroll_student(12, CURDATE(), 100000003, 1001, @result);
SELECT @result;

-- Try enrolling into a section that doesn't exist (should error)
CALL enroll_student(12, CURDATE(), 100000003, 9999, @result);
SELECT @result;

-- Assign an instructor to a section
CALL assign_instructor_to_class(6, 1002, 1001, @result);
SELECT @result;

-- Try assigning the same instructor again (should error)
CALL assign_instructor_to_class(7, 1002, 1001, @result);
SELECT @result;

-- Drop a student from a section (pass the enrollment_id)
CALL drop_student_from_section(11, @result);
SELECT @result;

-- Try dropping an enrollment that doesn't exist (should error)
CALL drop_student_from_section(999, @result);
SELECT @result;

-- Give a grade to an enrollment
CALL give_grade(1, 'A', @result);
SELECT @result;

-- Try an invalid grade (should error)
CALL give_grade(1, 'Z', @result);
SELECT @result;

-- Grading an enrollment that doesn't exist (should error)
CALL give_grade(999, 'B+', @result);
SELECT @result;