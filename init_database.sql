CREATE TABLE IF NOT EXISTS USER_ (
    userId INT PRIMARY KEY,
    name_ VARCHAR(100) NOT NULL,
    surname VARCHAR(100) NOT NULL,
    password VARCHAR(256) NOT NULL,
    email VARCHAR(100) NOT NULL
);

CREATE TABLE IF NOT EXISTS JURY (
    juryId INT PRIMARY KEY,
    isApproved BOOLEAN,
    juryName VARCHAR(100) NOT NULL,
    institution VARCHAR(180) NOT NULL,
    department VARCHAR(180) NOT NULL,
    phoneNumber VARCHAR(180) NOT NULL,
    appointmentStatus BOOLEAN,
    FOREIGN KEY(juryId) REFERENCES User_(userId)
);

CREATE TABLE IF NOT EXISTS Student (
    studentId INT PRIMARY KEY,
    isApproved BOOLEAN,
    semester INT,
    programName VARCHAR(180),
    thesisTopic VARCHAR(180),
    graduationStatus VARCHAR(180),
    FOREIGN KEY(studentId) REFERENCES User_(userId)
);

CREATE TABLE IF NOT EXISTS Advisor (
    advisorId INT,
    doctoralSpeciality VARCHAR (180),
    FOREIGN KEY(advisorId) REFERENCES User_(advisorId)
);

CREATE TABLE IF NOT EXISTS Instructor (
    advisorId INTEGER PRIMARY KEY,
    studentId INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS Reccomended (
    advisorId INTEGER PRIMARY KEY,
    studentId INTEGER PRIMARY KEY
);
