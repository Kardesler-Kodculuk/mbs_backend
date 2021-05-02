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
    has_proposed BOOLEAN,
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
    recommendation_id INTEGER PRIMARY KEY,
    student_id INTEGER,
    advisor_id INTEGER,
    FOREIGN KEY (student_id) REFERENCES Student(student_id),
    FOREIGN KEY (advisor_id) REFERENCES Advisor(advisor_id)
);

CREATE TABLE IF NOT EXISTS Proposal (
    proposal_id INTEGER PRIMARY KEY,
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
INSERT INTO Student VALUES (0, TRUE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', 'NA');
INSERT INTO USER_ VALUES (1, 'Kathleen', 'Booth', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'advisortest@iyte.edu.tr');
INSERT INTO Advisor VALUES (1, 'Computer Engineering', 'Systems Programming');
INSERT INTO Instructor VALUES (0, 0, 1);

/**
    A new advisor and two students who have proposed to him.
 */
INSERT INTO USER_ VALUES (3, 'Harry', 'Bouwman', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'bouwman@iyte.edu.tr');
INSERT INTO Advisor VALUES (3, 'Computer Engineering', 'Operating Systems');
INSERT INTO USER_ VALUES (4, 'Sherlock', 'Holmes', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'holmes@std.iyte.edu.tr');
INSERT INTO Student VALUES (4, FALSE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', 'NA');
INSERT INTO USER_ VALUES (5, 'John', 'Watson', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'watson@std.iyte.edu.tr');
INSERT INTO Student VALUES (5, FALSE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', 'NA');
INSERT INTO Proposal VALUES (0, 4, 3);
INSERT INTO Proposal VALUES (1, 5, 3);


/**
  This is a student without an advisor, but she is recommended two.
 */
INSERT INTO User_ VALUES (2, 'Barbara', 'Liskov', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'studenttest2@std.iyte.edu.tr');
INSERT INTO Student VALUES (2, FALSE, FALSE, 2, 'Computer Engineering', NULL, 'NA', 'NA');
INSERT INTO Recommended VALUES (0, 2, 1);
INSERT INTO Recommended VALUES (1, 2, 3);

/**
  In the end, in this Test set, we have two advisors:
  Advisor 1: Kathleen Booth, who is recommended to Barbara Liskov and is the advisor of Scott Aaronson.
  Advisor 2: Hary Bouwman, who is recommended to Barbara Liskov and has pending proposals from John Watson and
    Sherlock Holmes.
 */