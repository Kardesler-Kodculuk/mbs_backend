
/**
 ########################################
 #             USER TABLES              #
 ########################################
 */

CREATE TABLE IF NOT EXISTS Department (
    department_id INTEGER PRIMARY KEY,
    department_name TEXT UNIQUE,
    turkish_department_name TEXT UNIQUE
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

CREATE TABLE IF NOT EXISTS DBR (
    dbr_id INTEGER PRIMARY KEY,
    FOREIGN KEY(dbr_id) REFERENCES User_(user_id)
);

CREATE TABLE IF NOT EXISTS Student (
    student_id INTEGER PRIMARY KEY,
    is_approved BOOLEAN,
    has_proposed BOOLEAN,
    semester INTEGER,
    program_name TEXT,
    thesis_topic TEXT,
    graduation_status TEXT,
    is_thesis_sent BOOLEAN,
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
    original_name TEXT,
    plagiarism_ratio INTEGER,
    thesis_topic TEXT,
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
    dissertation_id INTEGER,
    jury_id INTEGER,
    evaluation
                                      CHECK ( evaluation IN ('Correction', 'Rejected', 'Approved') ),
                                          FOREIGN KEY (dissertation_id) REFERENCES Dissertation(dissertation_id)
);

/**
  This is a pair of Student and Advisors that has instructor relationship
    between each other.
 */
INSERT INTO USER_ VALUES (0, 'Scott', 'Aaronson', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'studenttest@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (0, TRUE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', FALSE);
INSERT INTO USER_ VALUES (1, 'Kathleen', 'Booth', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'advisortest@iyte.edu.tr', 0);
INSERT INTO Advisor VALUES (1, 'Systems Programming');
INSERT INTO Instructor VALUES (0, 0, 1);

/**
    A new advisor and two students who have proposed to him.
 */

INSERT INTO Department VALUES (0, 'Computer Engineering', 'Bilgisayar Mühendisliği');

INSERT INTO USER_ VALUES (3, 'Harry', 'Bouwman', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'bouwman@iyte.edu.tr', 0);
INSERT INTO Advisor VALUES (3, 'Operating Systems');
INSERT INTO USER_ VALUES (4, 'Sherlock', 'Holmes', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'holmes@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (4, FALSE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', FALSE);
INSERT INTO USER_ VALUES (5, 'John', 'Watson', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'watson@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (5, FALSE, TRUE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', FALSE);
INSERT INTO Proposal VALUES (0, 4, 3);
INSERT INTO Proposal VALUES (1, 5, 3);


/**
  This is a student without an advisor, but she is recommended two.
 */
INSERT INTO User_ VALUES (2, 'Barbara', 'Liskov', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'studenttest2@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (2, FALSE, FALSE, 2, 'Computer Engineering', 'Graph Visualisation', 'NA', FALSE);
INSERT INTO Recommended VALUES (0, 2, 1);
INSERT INTO Recommended VALUES (1, 2, 3);

INSERT INTO USER_ VALUES (6, 'Conan', 'Doyle', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'doyle@iyte.edu.tr', 0);
INSERT INTO Advisor VALUES (6, 'Operating Systems');
INSERT INTO User_ VALUES (7, 'James', 'Moriarty', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'moriarty@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (7, TRUE, TRUE, 2, 'Computer Engineering', NULL, 'NA', FALSE);
INSERT INTO User_ VALUES (8, 'Mycroft', 'Holmes', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'holmes2@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (8, TRUE, TRUE, 2, 'Computer Engineering', NULL, 'NA', FALSE);
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
INSERT INTO Student VALUES (10, FALSE, TRUE, 2, 'Computer Engineering', 'Artificial Intelligence', 'NA', FALSE);
INSERT INTO User_ VALUES (11, 'Arthur', 'Hastings', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'hastings@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (11, FALSE, TRUE, 2, 'Computer Engineering', 'Robotics', 'NA', FALSE);
INSERT INTO User_ VALUES (12, 'Jane', 'Marple', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'marple@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (12, FALSE, TRUE, 2, 'Computer Engineering', 'Fault Tollerance', 'NA', FALSE);
INSERT INTO User_ VALUES (13, 'Harold', 'Japp', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'japp@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (13, FALSE, TRUE, 2, 'Computer Engineering', 'Embedded Systems', 'NA', FALSE);
INSERT INTO User_ VALUES (14, 'Raymond', 'West', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'west@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (14, FALSE, TRUE, 2, 'Computer Engineering', 'Assembly Language', 'NA', FALSE);

INSERT INTO Proposal VALUES (2, 10, 9);
INSERT INTO Proposal VALUES (3, 11, 9);
INSERT INTO Proposal VALUES (4, 12, 9);
INSERT INTO Proposal VALUES (5, 13, 9);
INSERT INTO Proposal VALUES (6, 14, 9);

INSERT INTO User_ VALUES (15, 'Sophia', 'Leonides', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'leonides@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (15, FALSE, FALSE, 2, 'Computer Engineering', NULL, 'NA', FALSE);

INSERT INTO Recommended VALUES (2, 15, 9);


/** THESIS TEST USERS */
INSERT INTO USER_ VALUES (16, 'Ariadne', 'Oliver', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'oliver@iyte.edu.tr', 0);
INSERT INTO Advisor VALUES (16, 'Character Encoding');
INSERT INTO Jury VALUES (16, TRUE, 'Izmir Institute of Technology', '+90 5XX XXX XX XX', FALSE);
INSERT INTO User_ VALUES (17, 'Jane', 'Grey', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'grey@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (17, TRUE, TRUE, 2, 'Computer Engineering', 'Artificial Intelligence', 'NA', FALSE);
INSERT INTO Thesis VALUES (0, 'theses/grey_thesis_example0.pdf', 'grey_thesis_example0.pdf', 15, 'Artificial Intelligence', 1621129273);
INSERT INTO Has VALUES (0, 0, 17); /** Add an example thesis.*/
INSERT INTO Thesis VALUES (1, 'theses/grey_thesis_example1.pdf', 'grey_thesis_example1.pdf', 10, 'Artificial Intelligence', 1621129275);
INSERT INTO Has VALUES (1, 1, 17); /** Add another example thesis.*/
INSERT INTO Instructor VALUES (5, 17, 16);

/** DBR Test Users */
INSERT INTO Department VALUES (1, 'History', 'Tarih');
INSERT INTO Department VALUES (2, 'Not Available', '-');
INSERT INTO User_ VALUES (18, 'Roddy', 'Welman', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'welman@pers.iyte.edu.tr', 0);
INSERT INTO DBR VALUES (18);
INSERT INTO User_ VALUES (19, 'Peter', 'Lord', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'lord@pers.iyte.edu.tr', 1);
INSERT INTO DBR VALUES (19);
INSERT INTO User_ VALUES (20, 'Eileen', 'O''Brien', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'obrien@metu.edu.tr', 2);
INSERT INTO Jury VALUES (20, TRUE, 'Middle Eastern Technical University', '+90 5XX XXX XX XX', TRUE);

INSERT INTO Dissertation VALUES (0, 1621129275, TRUE); /** Add a dissertation. */
INSERT INTO Defending VALUES (0, 0, 17);
INSERT INTO Dissertation VALUES (1, 1621129275, TRUE); /** Add a dissertation. */
INSERT INTO Defending VALUES (1, 1, 15); /** Another one. */
INSERT INTO Member VALUES (0, 0, 20);
INSERT INTO Member VALUES (1, 1, 20);
INSERT INTO Member VALUES (6, 0, 16);

INSERT INTO User_ VALUES (21, 'Elinor Katharine', 'Carlisle', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'katharine@std.iyte.edu.tr', 1);
INSERT INTO Student VALUES (21, TRUE, TRUE, 2, 'Medieval History', 'Danelaw', 'NA', FALSE);
INSERT INTO User_ VALUES (22, 'Mary', 'Gerrard', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'gerrard@std.iyte.edu.tr', 1);
INSERT INTO Student VALUES (22, TRUE, TRUE, 2, 'Roman History', 'Third Century Crisis', 'NA', FALSE);

INSERT INTO User_ VALUES (23, 'Jessie', 'Hopkins', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'hopkins@iyte.edu.tr', 1);
INSERT INTO Advisor VALUES (23, 'Bronze Age Collapse');
INSERT INTO JURY VALUES (23, TRUE, 'Izmir Institute of Technology', '+90 5XX XXX XX XX', FALSE);

INSERT INTO User_ VALUES (24, 'Ted', 'Bigland', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'bigland@iyte.edu.tr', 1);
INSERT INTO Advisor VALUES (24, 'Persian Empire');
INSERT INTO JURY VALUES (24, TRUE, 'Izmir Institute of Technology', '+90 5XX XXX XX XX', FALSE);

INSERT INTO User_ VALUES (25, 'Emma', 'Bishop', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'bishop@iyte.edu.tr', 1);
INSERT INTO Advisor VALUES (25, 'Julio-Claudian Dynasty');
INSERT INTO JURY VALUES (25, TRUE, 'Izmir Institute of Technology', '+90 5XX XXX XX XX', FALSE);


INSERT INTO Instructor VALUES (3, 21, 23);
INSERT INTO Instructor VALUES (4, 22, 23);
INSERT INTO Dissertation VALUES (2, 1621129276, TRUE);
INSERT INTO Member VALUES (2, 2, 23);
INSERT INTO Defending VALUES (2, 2, 22);
INSERT INTO Member VALUES (3, 2, 20);
INSERT INTO Evaluation VALUES (0, 2, 23, 'Approved');

/**
  * So second student defends a thesis and both are instructors to Jessie Hopkins
 */

INSERT INTO Dissertation VALUES (3, 1621129276, FALSE);
INSERT INTO Member VALUES (4, 3, 23);
INSERT INTO Defending VALUES (3, 3, 21);
INSERT INTO Member VALUES (5, 3, 20);

INSERT INTO User_ VALUES (26, 'Bob', 'Nathan', '$pbkdf2-sha256$29000$xNh7j3HunXMuxRgDAGBMyQ$Z8D9vpTaauX/jIxrgxtCkba83F/rVI1LeYAtpHCIhRg', 'nathan@std.iyte.edu.tr', 0);
INSERT INTO Student VALUES (26, TRUE, TRUE, 2, 'Computer Engineering', 'Artificial Intelligence', 'NA', FALSE);
INSERT INTO Instructor VALUES (6, 26, 16);
INSERT INTO Thesis VALUES (2, 'theses/bob_nathan_thesis.pdf', 'bob_nathan_thesis.pdf', 10, 'Artificial Intelligence', 1621129275);
INSERT INTO Has VALUES (2, 2, 26); /** Add another example thesis.*/
