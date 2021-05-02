CREATE TABLE IF NOT EXISTS USER_ (
    user_id INTEGER PRIMARY KEY,
    name_ TEXT NOT NULL,
    surname TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS JURY (
    jury_id INTEGER PRIMARY KEY,
    is_approved BOOLEAN,
    jury_name TEXT NOT NULL,
    institution TEXT NOT NULL,
    department TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    appointment_status BOOLEAN,
    FOREIGN KEY(jury_id) REFERENCES User_(user_id)
);

CREATE TABLE IF NOT EXISTS Student (
    student_id INTEGER PRIMARY KEY,
    is_approved BOOLEAN,
    semester INTEGER,
    program_name TEXT,
    thesis_topic TEXT,
    graduation_status TEXT,
    jury_tss_decision TEXT,
    FOREIGN KEY(student_id) REFERENCES User_(user_id)
);

CREATE TABLE IF NOT EXISTS Advisor (
    advisor_id INTEGER PRIMARY KEY,
    department TEXT,
    doctoral_speciality TEXT,
    FOREIGN KEY(advisor_id) REFERENCES User_(user_id)
);

CREATE TABLE IF NOT EXISTS Instructor (
    id_ INTEGER PRIMARY KEY,
    student_id INTEGER UNIQUE, /** There can only be one advisor per student. */
    advisor_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (advisor_id) REFERENCES Advisor(advisor_id)
);

CREATE TABLE IF NOT EXISTS Recommended (
    id_ INTEGER PRIMARY KEY,
    student_id INTEGER,
    advisor_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (advisor_id) REFERENCES Advisor(advisor_id)
);

CREATE TABLE IF NOT EXISTS Proposal (
    id_ INTEGER PRIMARY KEY,
    student_id INTEGER UNIQUE,
    advisor_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (advisor_id) REFERENCES Advisor(advisor_id)
);
/**
  This is a pair of Student and Advisors that has instructor relationship
    between each other.
 */
INSERT INTO USER_ VALUES (0, 'Scott', 'Aaronson', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'studenttest@std.iyte.edu.tr');
INSERT INTO Student VALUES (0, FALSE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', 'NA');
INSERT INTO USER_ VALUES (1, 'Kathleen', 'Booth', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'advisortest@iyte.edu.tr');
INSERT INTO Advisor VALUES (1, 'Computer Engineering', 'Systems Programming');
INSERT INTO Instructor(student_id, advisor_id) VALUES (0, 1);


/**
  This is a student without an advisor, but she is recommended one.
 */
INSERT INTO User_ VALUES (2, 'Barbara', 'Liskov', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'studenttest2@std.iyte.edu.tr');
INSERT INTO Student VALUES (2, FALSE, 2, 'Computer Engineering', NULL, 'NA', 'NA');
INSERT INTO Recommended(student_id, advisor_id) VALUES (2, 1);