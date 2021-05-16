
/**
 ########################################
 #             USER TABLES              #
 ########################################
 */

CREATE TABLE IF NOT EXISTS Department (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT UNIQUE
);

CREATE TABLE IF NOT EXISTS USER_ (
    user_id INTEGER PRIMARY KEY,
    name_ TEXT NOT NULL,
    surname TEXT NOT NULL,
    password TEXT NOT NULL,
    email TEXT NOT NULL,
    department_id INTEGER, /** All users in the second iteration have a department. */
    FOREIGN KEY (department_id) REFERENCES Department(department_id)
);


CREATE TABLE IF NOT EXISTS JURY (
    jury_id INTEGER PRIMARY KEY,
    is_approved BOOLEAN,
    institution TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    is_appointed BOOLEAN,
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
 ########################################
 #             THESIS TABLES            #
 ########################################
 */

CREATE TABLE IF NOT EXISTS Thesis (
    thesis_id INTEGER PRIMARY KEY,
    file_path TEXT UNIQUE,
    plagiarism_ratio INTEGER,
    thesis_topic TEXT,
    due_date INTEGER,
    submission_date INTEGER
);


CREATE TABLE IF NOT EXISTS Has(
    has_id INTEGER PRIMARY KEY,
    thesis_id INTEGER,
    student_id INTEGER,
    FOREIGN KEY (thesis_id) REFERENCES Thesis(thesis_id),
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
);


/** These are the relationships and tables about Dissertations */

CREATE TABLE IF NOT EXISTS Dissertation(
    dissertation_id INTEGER PRIMARY KEY,
    jury_date INTEGER,
    is_approved BOOLEAN
);

CREATE TABLE IF NOT EXISTS Member (
    member_id INTEGER PRIMARY KEY,
    dissertation_id INTEGER,
    jury_id INTEGER,
    FOREIGN KEY (dissertation_id) REFERENCES Dissertation(dissertation_id),
    FOREIGN KEY (jury_id) REFERENCES JURY(jury_id)
);

CREATE TABLE IF NOT EXISTS Defending (
    defending_id INTEGER PRIMARY KEY,
    dissertation_id INTEGER,
    student_id INTEGER,
    FOREIGN KEY (dissertation_id) REFERENCES Dissertation(dissertation_id),
    FOREIGN KEY (student_id) REFERENCES Student(student_id)
);

CREATE TABLE IF NOT EXISTS Evaluation (
    evaluation_id INTEGER PRIMARY KEY,
    jury_id INTEGER,
    evaluation_status TEXT
                                      CHECK ( evaluation_status IN ('Correction', 'Rejected', 'Approved') )
);

/**
  This is a pair of Student and Advisors that has instructor relationship
    between each other.
 */
INSERT INTO USER_ VALUES (0, 'Scott', 'Aaronson', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'studenttest@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (0, TRUE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', 'NA');
INSERT INTO USER_ VALUES (1, 'Kathleen', 'Booth', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'advisortest@iyte.edu.tr', 0);
INSERT INTO Advisor VALUES (1, 'Systems Programming');
INSERT INTO Instructor VALUES (0, 0, 1);

/**
    A new advisor and two students who have proposed to him.
 */

INSERT INTO Department VALUES (0, 'Computer Engineering');

INSERT INTO USER_ VALUES (3, 'Harry', 'Bouwman', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'bouwman@iyte.edu.tr', 0);
INSERT INTO Advisor VALUES (3, 'Operating Systems');
INSERT INTO USER_ VALUES (4, 'Sherlock', 'Holmes', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'holmes@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (4, FALSE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', 'NA');
INSERT INTO USER_ VALUES (5, 'John', 'Watson', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'watson@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (5, FALSE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', 'NA');
INSERT INTO Proposal VALUES (0, 4, 3);
INSERT INTO Proposal VALUES (1, 5, 3);


/**
  This is a student without an advisor, but she is recommended two.
 */
INSERT INTO User_ VALUES (2, 'Barbara', 'Liskov', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'studenttest2@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (2, FALSE, FALSE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', 'NA');
INSERT INTO Recommended VALUES (0, 2, 1);
INSERT INTO Recommended VALUES (1, 2, 3);

INSERT INTO USER_ VALUES (6, 'Conan', 'Doyle', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'doyle@iyte.edu.tr', 0);
INSERT INTO Advisor VALUES (6, 'Operating Systems');
INSERT INTO User_ VALUES (7, 'James', 'Moriarty', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'moriarty@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (7, TRUE, TRUE, 2, 'Computer Engineering', NULL, 'NA', 'NA');
INSERT INTO User_ VALUES (8, 'Mycroft', 'Holmes', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'holmes2@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (8, TRUE, TRUE, 2, 'Computer Engineering', NULL, 'NA', 'NA');
INSERT INTO Instructor VALUES(1, 7, 6);
INSERT INTO Instructor VALUES(2, 8, 6);

/**
  In the end, in this Test set, we have two advisors:
  Advisor 1: Kathleen Booth, who is recommended to Barbara Liskov and is the advisor of Scott Aaronson.
  Advisor 2: Hary Bouwman, who is recommended to Barbara Liskov and has pending proposals from John Watson and
    Sherlock Holmes.
  Advisor 3: Conan Doyle, who is advisor to Mycroft Holmes and James Moriarty
 */

INSERT INTO USER_ VALUES (9, 'Agatha', 'Christie', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'christie@iyte.edu.tr', 0);
INSERT INTO Advisor VALUES (9, 'Operating Systems');
INSERT INTO User_ VALUES (10, 'Hercule', 'Poirot', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'poirot@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (10, FALSE, TRUE, 2, 'Computer Engineering', 'Artificial Intelligence', 'NA', 'NA');
INSERT INTO User_ VALUES (11, 'Arthur', 'Hastings', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'hastings@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (11, FALSE, TRUE, 2, 'Computer Engineering', 'Robotics', 'NA', 'NA');
INSERT INTO User_ VALUES (12, 'Jane', 'Marple', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'marple@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (12, FALSE, TRUE, 2, 'Computer Engineering', 'Fault Tollerance', 'NA', 'NA');
INSERT INTO User_ VALUES (13, 'Harold', 'Japp', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'japp@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (13, FALSE, TRUE, 2, 'Computer Engineering', 'Embedded Systems', 'NA', 'NA');
INSERT INTO User_ VALUES (14, 'Raymond', 'West', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'west@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (14, FALSE, TRUE, 2, 'Computer Engineering', 'Assembly Language', 'NA', 'NA');

INSERT INTO Proposal VALUES (2, 10, 9);
INSERT INTO Proposal VALUES (3, 11, 9);
INSERT INTO Proposal VALUES (4, 12, 9);
INSERT INTO Proposal VALUES (5, 13, 9);
INSERT INTO Proposal VALUES (6, 14, 9);

INSERT INTO User_ VALUES (15, 'Sophia', 'Leonides', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'leonides@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (15, FALSE, FALSE, 2, 'Computer Engineering', NULL, 'NA', 'NA');

INSERT INTO Recommended VALUES (2, 15, 9);