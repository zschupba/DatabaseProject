create table building (
    building_id     NUMERIC(6,0)    PRIMARY KEY,
    name            VARCHAR(32)     NOT NULL,
    address         VARCHAR(64)     NOT NULL
);

create table department (
    dept_id         NUMERIC(6,0)    PRIMARY KEY,
    dept_name       VARCHAR(16)     NOT NULL,
    office_building NUMERIC(6,0),
    budget          NUMERIC(12,2),
    CONSTRAINT fk_dept_building FOREIGN KEY (office_building) REFERENCES building(building_id)
);

create table student (
    student_id          NUMERIC(9,0)    PRIMARY KEY,
    first_name          VARCHAR(16)     NOT NULL,
    last_name           VARCHAR(16)     NOT NULL,
    email               VARCHAR(32)     NOT NULL UNIQUE,
    enrollment_date     DATE,
    enrollment_status   BOOLEAN         NOT NULL DEFAULT TRUE,
    dept_id             NUMERIC(6,0),
    CONSTRAINT fk_student_dept FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

create table instructor (
    instructor_id   NUMERIC(8,0)    PRIMARY KEY,
    first_name      VARCHAR(16)     NOT NULL,
    last_name       VARCHAR(16)     NOT NULL,
    salary          NUMERIC(8,2),
    hire_date       DATE,
    dept_id         NUMERIC(6,0),
    CONSTRAINT fk_instructor_dept FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

create table useraccount (
    user_id         NUMERIC(10,0)   PRIMARY KEY,
    username        VARCHAR(12)     NOT NULL UNIQUE,
    password        VARCHAR(16)     NOT NULL,
    role            VARCHAR(10)     NOT NULL,
    student_id      NUMERIC(9,0),
    instructor_id   NUMERIC(8,0),
    created_at      DATETIME        NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_login      DATETIME,
    CONSTRAINT fk_user_student    FOREIGN KEY (student_id)    REFERENCES student(student_id),
    CONSTRAINT fk_user_instructor FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id),
    CONSTRAINT chk_user_role CHECK (
        (role = 'student'    AND student_id    IS NOT NULL AND instructor_id IS NULL) OR
        (role = 'instructor' AND instructor_id IS NOT NULL AND student_id    IS NULL) OR
        (role = 'admin'      AND student_id    IS NULL     AND instructor_id IS NULL)
    )
);

create table classroom (
    classroom_id    NUMERIC(6,0)    PRIMARY KEY,
    building_id     NUMERIC(6,0)    NOT NULL,
    room_number     NUMERIC(4,0)    NOT NULL,
    capacity        NUMERIC(3,0),
    CONSTRAINT fk_classroom_building FOREIGN KEY (building_id) REFERENCES building(building_id)
);

create table timeslot (
    slot_id         NUMERIC(6,0)    PRIMARY KEY,
    day_of_week     VARCHAR(8)      NOT NULL,
    start_time      TIME            NOT NULL,
    end_time        TIME            NOT NULL
);

create table course (
    course_code     NUMERIC(6,0)    PRIMARY KEY,
    title           VARCHAR(50)     NOT NULL,
    credits         NUMERIC(2,0)    NOT NULL,
    dept_id         NUMERIC(6,0),
    CONSTRAINT fk_course_dept FOREIGN KEY (dept_id) REFERENCES department(dept_id)
);

create table prereq (
    course_code         NUMERIC(6,0)    NOT NULL,
    prereq_course_id    NUMERIC(6,0)    NOT NULL,
    req_type            VARCHAR(9),
    PRIMARY KEY (course_code, prereq_course_id),
    CONSTRAINT fk_prereq_course  FOREIGN KEY (course_code)      REFERENCES course(course_code),
    CONSTRAINT fk_prereq_prereq  FOREIGN KEY (prereq_course_id) REFERENCES course(course_code)
);

create table section (
    section_id      NUMERIC(6,0)    PRIMARY KEY,
    semester        CHAR(6)         NOT NULL,
    year            NUMERIC(4,0)    NOT NULL,
    capacity        NUMERIC(3,0),
    course_code     NUMERIC(6,0)    NOT NULL,
    classroom_id    NUMERIC(6,0),
    slot_id         NUMERIC(6,0),
    CONSTRAINT fk_section_course    FOREIGN KEY (course_code)  REFERENCES course(course_code),
    CONSTRAINT fk_section_classroom FOREIGN KEY (classroom_id) REFERENCES classroom(classroom_id),
    CONSTRAINT fk_section_timeslot  FOREIGN KEY (slot_id)      REFERENCES timeslot(slot_id)
);

create table teaches (
    teaches_id      NUMERIC(6,0)    PRIMARY KEY,
    instructor_id   NUMERIC(8,0)    NOT NULL,
    section_id      NUMERIC(6,0)    NOT NULL,
    CONSTRAINT fk_teaches_instructor FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id),
    CONSTRAINT fk_teaches_section    FOREIGN KEY (section_id)    REFERENCES section(section_id)
);

create table enrolls (
    enrollment_id   NUMERIC(6,0)    PRIMARY KEY,
    grade           CHAR(2),
    date_enrolled   DATE            NOT NULL,
    student_id      NUMERIC(9,0)    NOT NULL,
    section_id      NUMERIC(6,0)    NOT NULL,
    CONSTRAINT fk_enrolls_student FOREIGN KEY (student_id) REFERENCES student(student_id),
    CONSTRAINT fk_enrolls_section FOREIGN KEY (section_id) REFERENCES section(section_id)
);

create table advisor (
    advisor_id      NUMERIC(6,0)    PRIMARY KEY,
    start_date      DATE,
    student_id      NUMERIC(9,0)    NOT NULL,
    instructor_id   NUMERIC(8,0)    NOT NULL,
    CONSTRAINT fk_advisor_student    FOREIGN KEY (student_id)    REFERENCES student(student_id),
    CONSTRAINT fk_advisor_instructor FOREIGN KEY (instructor_id) REFERENCES instructor(instructor_id)
);