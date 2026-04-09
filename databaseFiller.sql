-- Building
INSERT INTO building VALUES (1, 'Science Hall',    '100 Loop rd');
INSERT INTO building VALUES (2, 'Liberal Arts',    '200 Summit st');
INSERT INTO building VALUES (3, 'Engineering Bldg','300 East Main st');
 
-- Departments
INSERT INTO department VALUES (10, 'CompSci',   1, 500000.00);
INSERT INTO department VALUES (20, 'Math',       2, 300000.00);
INSERT INTO department VALUES (30, 'Engineering',3, 750000.00);
 
-- Instructors
INSERT INTO instructor VALUES (1001, 'Mel',  'Din',  85000.00, '2018-08-01', 10);
INSERT INTO instructor VALUES (1002, 'Michael',  'Walters', 92000.00, '2015-01-15', 20);
INSERT INTO instructor VALUES (1003, 'Giovanni', 'Lastname',    78000.00, '2020-09-01', 30);
 
-- Students
INSERT INTO student VALUES (100000001, 'James',   'Smith',  'jsmith@kent.edu',   '2022-08-20', TRUE, 10);
INSERT INTO student VALUES (100000002, 'Caden',  'Butt',  'cbutt@kent.edu',   '2022-08-20', TRUE, 10);
INSERT INTO student VALUES (100000003, 'Marcus',  'Hill',    'mhill@kent.edu',     '2021-08-18', TRUE, 20);
INSERT INTO student VALUES (100000004, 'Olivia',  'Brooks',  'obrooks@kent.edu',   '2023-01-10', TRUE, 20);
INSERT INTO student VALUES (100000005, 'Ethan',   'Ross',    'eross@kent.edu',     '2021-08-18', TRUE, 30);
INSERT INTO student VALUES (100000006, 'Ava',     'Mitchell','amitchell@kent.edu', '2022-08-20', TRUE, 30);
INSERT INTO student VALUES (100000007, 'Liam',    'Foster',  'lfoster@kent.edu',   '2023-01-10', TRUE, 10);
INSERT INTO student VALUES (100000008, 'Emma',    'Gray',    'egray@kent.edu',     '2022-08-20', TRUE, 20);
INSERT INTO student VALUES (100000009, 'Noah',    'Bennett', 'nbennett@kent.edu',  '2021-08-18', TRUE, 30);
INSERT INTO student VALUES (100000010, 'Isabella','Price',   'iprice@kent.edu',    '2023-08-21', TRUE, 10);
 
-- User Accounts
INSERT INTO useraccount VALUES (9000000001, 'meldin',     'pass1234', 'instructor', NULL, 1001, , NULL);
INSERT INTO useraccount VALUES (9000000002, 'mwalters',    'pass1234', 'instructor', NULL, 1002, NULL, NULL);
INSERT INTO useraccount VALUES (9000000003, 'glastnam',       'pass1234', 'instructor', NULL, 1003, NULL, NULL);
INSERT INTO useraccount VALUES (9000000004, 'jsmith',     'pass1234', 'student',    100000001, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000005, 'cbutt',     'pass1234', 'student',    100000002, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000006, 'mhill',       'pass1234', 'student',    100000003, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000007, 'obrooks',     'pass1234', 'student',    100000004, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000008, 'eross',       'pass1234', 'student',    100000005, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000009, 'amitchell',   'pass1234', 'student',    100000006, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000010, 'lfoster',     'pass1234', 'student',    100000007, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000011, 'egray',       'pass1234', 'student',    100000008, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000012, 'nbennett',    'pass1234', 'student',    100000009, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000013, 'iprice',      'pass1234', 'student',    100000010, NULL, NULL, NULL);
INSERT INTO useraccount VALUES (9000000014, 'admin',       'adminpass','admin',      NULL,      NULL, NULL, NULL);
 
-- Classrooms
INSERT INTO classroom VALUES (201, 1, 101, 30);
INSERT INTO classroom VALUES (202, 1, 102, 25);
INSERT INTO classroom VALUES (203, 2, 201, 40);
INSERT INTO classroom VALUES (204, 3, 301, 35);
 
-- Timeslots
INSERT INTO timeslot VALUES (1, 'Monday',    '08:00:00', '09:15:00');
INSERT INTO timeslot VALUES (2, 'Wednesday', '08:00:00', '09:15:00');
INSERT INTO timeslot VALUES (3, 'Tuesday',   '10:00:00', '11:15:00');
INSERT INTO timeslot VALUES (4, 'Thursday',  '10:00:00', '11:15:00');
INSERT INTO timeslot VALUES (5, 'Friday',    '13:00:00', '14:15:00');
 
-- Courses
INSERT INTO course VALUES (301, 'Intro to Programming',  3, 10);
INSERT INTO course VALUES (302, 'Data Structures',       3, 10);
INSERT INTO course VALUES (401, 'Calculus I',            4, 20);
INSERT INTO course VALUES (402, 'Linear Algebra',        3, 20);
INSERT INTO course VALUES (501, 'Circuits I',            3, 30);
 
-- Prerequisites
INSERT INTO prereq VALUES (302, 301, 'required');
INSERT INTO prereq VALUES (402, 401, 'required');
 
-- Sections 
INSERT INTO section VALUES (1001, 'Spring', 2025, 30, 301, 201, 1);
INSERT INTO section VALUES (1002, 'Spring', 2025, 25, 302, 202, 3);
INSERT INTO section VALUES (1003, 'Spring', 2025, 40, 401, 203, 2);
INSERT INTO section VALUES (1004, 'Spring', 2025, 35, 501, 204, 4);
 
-- Teaches 
INSERT INTO teaches VALUES (1, 1001, 1001);
INSERT INTO teaches VALUES (2, 1001, 1002);
INSERT INTO teaches VALUES (3, 1002, 1003);
INSERT INTO teaches VALUES (4, 1003, 1004);
 
-- Enrollments
INSERT INTO enrolls VALUES (1,  NULL, '2025-01-10', 100000001, 1001);
INSERT INTO enrolls VALUES (2,  NULL, '2025-01-10', 100000002, 1001);
INSERT INTO enrolls VALUES (3,  NULL, '2025-01-10', 100000007, 1001);
INSERT INTO enrolls VALUES (4,  NULL, '2025-01-11', 100000001, 1002);
INSERT INTO enrolls VALUES (5,  NULL, '2025-01-11', 100000003, 1003);
INSERT INTO enrolls VALUES (6,  NULL, '2025-01-11', 100000004, 1003);
INSERT INTO enrolls VALUES (7,  NULL, '2025-01-12', 100000005, 1004);
INSERT INTO enrolls VALUES (8,  NULL, '2025-01-12', 100000006, 1004);
INSERT INTO enrolls VALUES (9,  NULL, '2025-01-12', 100000008, 1003);
INSERT INTO enrolls VALUES (10, NULL, '2025-01-13', 100000009, 1004);
 
-- Advisors
INSERT INTO advisor VALUES (1, '2022-08-25', 100000001, 1001);
INSERT INTO advisor VALUES (2, '2022-08-25', 100000002, 1001);
INSERT INTO advisor VALUES (3, '2021-08-20', 100000003, 1002);
INSERT INTO advisor VALUES (4, '2021-08-20', 100000005, 1003);
 