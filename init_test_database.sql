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
    FOREIGN KEY(student_id) REFERENCES User_(user_id)
);

CREATE TABLE IF NOT EXISTS Advisor (
    advisor_id INTEGER PRIMARY KEY,
    doctoral_speciality TEXT,
    FOREIGN KEY(advisor_id) REFERENCES User_(user_id)
);

INSERT INTO USER_ VALUES (0, 'Scott', 'Aaronson', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'studenttest@std.iyte.edu.tr');
INSERT INTO Student VALUES (0, FALSE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA');