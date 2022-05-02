import mysql.connector
import environ





connection = mysql.connector.connect(
  host=("localhost"),
  user=("haruntaha"),
  password=("haruntaha"),
  database=("university_registration_system"),
)


cursor= connection.cursor()
#Create tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS Department (
  departmentId CHAR(10),
  name CHAR(30) NOT NULL,
  PRIMARY KEY (departmentId),
  UNIQUE (name)
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Instructor (
  username CHAR(20),
  title CHAR(20) NOT NULL,
  name CHAR(20) NOT NULL,
  surname CHAR(20) NOT NULL,
  email CHAR(40) NOT NULL,
  password CHAR(64) NOT NULL,
  departmentId CHAR(10) NOT NULL,
  UNIQUE (email),
  PRIMARY KEY (username),
  FOREIGN KEY (departmentId) REFERENCES Department(departmentId) ON DELETE NO ACTION ON UPDATE CASCADE,
  CONSTRAINT Title CHECK(
    STRCMP('Assistant Professor', title)= 0
    OR STRCMP('Associate Professor', title)= 0
    OR STRCMP('Professor', title)= 0
  )
);""")
cursor.execute("""
CREATE TABLE IF NOT EXISTS Student (
  username CHAR(20) PRIMARY KEY,
  studentId INTEGER NOT NULL,
  name CHAR(20) NOT NULL,
  surname CHAR(20) NOT NULL,
  email CHAR(40) NOT NULL,
  password CHAR(64) NOT NULL,
  departmentId CHAR(10) NOT NULL,
  gpa FLOAT DEFAULT 0,
  completedCredits INTEGER DEFAULT 0,
  UNIQUE (studentId),
  UNIQUE (email),
  FOREIGN KEY (departmentId) REFERENCES Department(departmentId) ON DELETE NO ACTION ON UPDATE CASCADE
);""")
connection.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Campus (
  name CHAR(20),
  PRIMARY KEY (name)
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Classroom (
  classroomId CHAR(6),
  capacity INTEGER NOT NULL,
  name CHAR(20) NOT NULL,
  PRIMARY KEY (classroomId),
  FOREIGN KEY(name) REFERENCES Campus(name) ON DELETE CASCADE ON UPDATE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS TimeSlot (
  slotNumber INTEGER,
  PRIMARY KEY (slotNumber),
  CONSTRAINT MaxSlotNumber CHECK (
    slotNumber >= 1
    AND slotNumber <= 10
  )
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Course (
  courseId CHAR(10),
  name CHAR(40) NOT NULL,
  quota INTEGER NOT NULL,
  credits INTEGER DEFAULT 0,
  classroomId CHAR(6) NOT NULL,
  slotNumber INTEGER NOT NULL,
  username CHAR(20) NOT NULL,
  PRIMARY KEY (courseId),
  UNIQUE(slotNumber, classroomId),
  FOREIGN KEY (classroomId) REFERENCES Classroom(classroomId) ON DELETE NO ACTION ON UPDATE CASCADE,
  FOREIGN KEY(username) REFERENCES Instructor(username) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY(slotNumber) REFERENCES TimeSlot(slotNumber) ON DELETE NO ACTION ON UPDATE CASCADE
);
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Grades (
  username CHAR(20) NOT NULL,
  courseId CHAR(10) NOT NULL,
  grade FLOAT,
  PRIMARY KEY (username, courseId),
  FOREIGN KEY(username) REFERENCES Student(username) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY(courseId) REFERENCES Course(courseId) ON DELETE NO ACTION ON UPDATE CASCADE
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS PreReq (
  courseId CHAR(10),
  prereqId CHAR(10),
  PRIMARY KEY (courseId, prereqId),
  FOREIGN KEY(courseId) REFERENCES Course(courseId),
  FOREIGN KEY(prereqId) REFERENCES Course(courseId),
  CONSTRAINT PreReqBigger CHECK(
    STRCMP(prereqId, courseId) < 0
  )
);""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS Whens (
  slotNumber INTEGER,
  classroomId CHAR(6),
  PRIMARY KEY (slotNumber, classroomId),
  FOREIGN KEY(slotNumber) REFERENCES TimeSlot(slotNumber) ON DELETE CASCADE ON UPDATE CASCADE,
  FOREIGN KEY(classroomId) REFERENCES Classroom(classroomId) ON DELETE CASCADE ON UPDATE CASCADE
);""")


cursor.execute("""
CREATE TABLE IF NOT EXISTS DatabaseManager (
  adminName CHAR(20),
  password CHAR(64) NOT NULL,
  PRIMARY KEY (adminName)
);""")

connection.commit()

cursor.execute("""DROP TRIGGER IF EXISTS ManagerUpdate;""")
connection.commit()
#Create the trigger for limiting 4 DATABASE MANAGERS
cursor.execute("""
CREATE TRIGGER ManagerUpdate BEFORE INSERT ON DatabaseManager FOR EACH ROW BEGIN
SELECT
  COUNT(*) INTO @cnt
FROM
  DatabaseManager;
IF @cnt > 3 THEN SIGNAL SQLSTATE '45000'
SET
  MESSAGE_TEXT = 'Manager Size is exceeded';
END IF;
END;""")

cursor.execute("""DROP TRIGGER IF EXISTS InstructorInsertChecker;""")
connection.commit()
cursor.execute("""
CREATE TRIGGER InstructorInsertChecker BEFORE INSERT ON Instructor FOR EACH ROW BEGIN IF(
    EXISTS(SELECT username FROM Student WHERE username = NEW.username)
) THEN SIGNAL SQLSTATE '45000'
SET
  MESSAGE_TEXT = 'The username you entered is used';
ElSEIF (EXISTS( SELECT Student.email FROM Student WHERE Student.email = NEW.email)
) THEN SIGNAL SQLSTATE '45000'
SET
  MESSAGE_TEXT = 'The email you entered is used';
END IF;
END;
""")

cursor.execute("""DROP TRIGGER IF EXISTS StudentInsertChecker;""")
connection.commit()
cursor.execute("""
CREATE TRIGGER StudentInsertChecker BEFORE INSERT ON Student FOR EACH ROW BEGIN IF(
  EXISTS(SELECT username FROM Instructor WHERE username = NEW.username)
) THEN SIGNAL SQLSTATE '45000'
SET
  MESSAGE_TEXT = 'The username you entered is used';
ELSEIF(
  EXISTS(SELECT Instructor.email FROM Instructor WHERE Instructor.email = NEW.email)
    ) THEN SIGNAL SQLSTATE '45000'
SET
  MESSAGE_TEXT = 'The email you entered is used';
END IF;
END;
""")

cursor.execute("""DROP TRIGGER IF EXISTS GradesUpdate;""")
connection.commit()
cursor.execute("""
CREATE TRIGGER GradesUpdate BEFORE
UPDATE
  ON GRADES FOR EACH ROW BEGIN IF NEW.grade < 0 THEN SIGNAL SQLSTATE '45000'
SET
  MESSAGE_TEXT = 'Grade cannot be less than 0';
ELSEIF(NEW.grade > 4) THEN SIGNAL SQLSTATE '45000'
SET
  MESSAGE_TEXT = 'Grade cannot be more than 4';
ELSEIF(
  (
    SELECT
      grade
    FROM
      Grades
    WHERE
      username = NEW.username
      AND courseId = NEW.courseId
  ) IS NULL
) THEN
UPDATE
  Student
SET
  completedCredits = completedCredits + (
    SELECT
      credits
    FROM
      Course
    WHERE
      courseId = NEW.courseId
  )
WHERE
  username = NEW.username;
END IF;
END;
""")


cursor.execute("""DROP TRIGGER IF EXISTS GpaUpdate;""")
connection.commit()
cursor.execute("""
CREATE TRIGGER GpaUpdate
AFTER
UPDATE
  ON GRADES FOR EACH ROW BEGIN
UPDATE
  Student
SET
  gpa = FORMAT((
    SELECT
      SUM(
        grade * (
          SELECT
            credits
          FROM
            Course
          WHERE
            Grades.courseId = Course.courseId
        )
      )
    FROM
      Grades
    WHERE
      username = NEW.username
  ) / completedCredits,2)
WHERE
  username = NEW.username;
end;

""")



cursor.execute("""DROP TRIGGER IF EXISTS QuotaChecker;""")
connection.commit()
cursor.execute("""
CREATE TRIGGER QuotaChecker
BEFORE INSERT ON Course FOR EACH ROW BEGIN
    IF((SELECT capacity FROM Classroom WHERE classroomId = NEW.classroomId) < NEW.quota)
        THEN SIGNAL SQLSTATE '45000'
SET
  MESSAGE_TEXT = 'Quota may not be greater than the capacity of the classroom';
END IF;
end;
""")

cursor.execute("""DROP TRIGGER IF EXISTS CheckPrereqForAddingNewCourse;""")
connection.commit()
cursor.execute("""
CREATE TRIGGER CheckPrereqForAddingNewCourse BEFORE INSERT
ON Grades FOR EACH ROW
BEGIN
   IF( (
   SELECT
      COUNT(*)
   FROM
      (
         SELECT
            prereqId AS 'Courses Not Yet Passed'
         FROM
            (
               SELECT
                  prereqId
               FROM
                  PreReq
               WHERE
                  courseId = NEW.courseId
               UNION ALL
               SELECT
                  courseId
               FROM
                  Grades
               WHERE
                  username = NEW.username
                  AND grade IS NOT NULL
            )
            newTable
         GROUP BY
            prereqId
         HAVING
            COUNT(*) = 2
      )
      AS `coursesNotPassed`) != (SELECT COUNT(*) FROM PreReq WHERE courseId = NEW.courseId) )
   THEN
      SIGNAL SQLSTATE '45000'
   SET
      MESSAGE_TEXT = 'Prerequisites for this course have not been passed';
END IF;
END;
""")


cursor.execute("""DROP PROCEDURE IF EXISTS AddStudent;""")
connection.commit()
cursor.execute("""
  CREATE PROCEDURE AddStudent(IN studentUsername CHAR(20), IN studentIdValue INTEGER, IN nameValue CHAR(20), IN surnameValue CHAR(20), IN emailValue CHAR(40), IN passwordValue TEXT, IN departmentIdValue CHAR(10))
  BEGIN
  INSERT INTO Student (username, studentId, name, surname, email, password, departmentId)
    SELECT
      
        studentUsername, studentIdValue, nameValue, surnameValue,
        emailValue, SHA2(passwordValue,256),
        departmentIdValue
      ;
  END;
""")
cursor.execute("""DROP PROCEDURE IF EXISTS AddInstructor;""")
connection.commit()
cursor.execute("""
  CREATE PROCEDURE AddInstructor(IN usernameValue CHAR(20), IN titleValue CHAR(20), IN nameValue CHAR(20), IN surnameValue CHAR(20), IN emailValue CHAR(40), IN passwordValue TEXT, IN departmentIdValue CHAR(10))
  BEGIN
  INSERT INTO Instructor(username, title, name, surname, email, password, departmentId)
    SELECT
      
        usernameValue, titleValue,
        nameValue, surnameValue, emailValue,
        SHA2(passwordValue,256), departmentIdValue
      ;
  END;
""")

cursor.execute("""DROP PROCEDURE IF EXISTS DeleteFromStudent;""")
connection.commit()
cursor.execute("""
  CREATE PROCEDURE DeleteFromStudent(IN studentIdValue INTEGER)
  BEGIN
    DELETE FROM Student WHERE Student.studentId=studentIdValue;
  END;
""")

cursor.execute("""DROP PROCEDURE IF EXISTS UpdateTitleOfInstructor;""")
connection.commit()
cursor.execute("""
  CREATE PROCEDURE UpdateTitleOfInstructor(IN newUsername CHAR(20),IN newTitle CHAR(20))
  BEGIN
    UPDATE Instructor
      SET title = newTitle
      WHERE Instructor.username=newUsername;
  END;
  """)

cursor.execute("""DROP PROCEDURE IF EXISTS AddCourse;""")
connection.commit()
cursor.execute("""
  CREATE PROCEDURE AddCourse(IN usernameValue CHAR(20),IN courseIdValue CHAR(10),IN nameValue CHAR(40), IN creditsValue INTEGER, IN classroomIdValue CHAR(6), IN slotNumberValue INTEGER, IN quotaValue INTEGER)
  BEGIN
    INSERT INTO Course (courseId, name, quota, credits, classroomId, slotNumber, username)
    VALUES
      (
       courseIdValue, nameValue, quotaValue, creditsValue,classroomIdValue,slotNumberValue,usernameValue
      );
    INSERT INTO Whens (slotNumber, classroomId)
    VALUES
      (
        slotNumberValue,
        classroomIdValue
      );
  END;
  """)

cursor.execute("""DROP PROCEDURE IF EXISTS AddPreReq;""")
connection.commit()
cursor.execute("""
  CREATE PROCEDURE AddPreReq(IN courseIdValue CHAR(10), IN preRequestIdValue CHAR(10))
  BEGIN
  INSERT INTO PreReq (courseId, prereqId)
    VALUES
      (
        courseIdValue, preRequestIdValue
      );
  END;
""")

cursor.execute("""DROP PROCEDURE IF EXISTS UpdateNameOfCourse;""")
connection.commit()
cursor.execute("""
  CREATE PROCEDURE UpdateNameOfCourse(IN courseIdValue CHAR(10),IN newName CHAR(40))
  BEGIN
    UPDATE Course
      SET name = newName
      WHERE Course.courseId=courseIdValue;
  END;
  """)
cursor.execute("""DROP PROCEDURE IF EXISTS GiveGrade;""")
connection.commit()
cursor.execute("""
  CREATE PROCEDURE GiveGrade(IN courseIdValue CHAR(10),IN userNameValue CHAR(20), IN newgrade FLOAT)
  BEGIN
    UPDATE Grades
      SET grade=newgrade
      WHERE Grades.courseId=courseIdValue AND Grades.username=userNameValue;
  END;
  """)


cursor.execute("""DROP PROCEDURE IF EXISTS Filter;""")
connection.commit()

cursor.execute("""
  CREATE PROCEDURE Filter(IN xdepartmentId CHAR(10),IN campusname CHAR(20), IN minCredits INTEGER, IN maxCredits INTEGER)
  BEGIN
    SELECT Course.courseId, Course.name, Instructor.surname, Instructor.departmentId, credits, Course.classroomId, Course.slotNumber, Course.quota, prereqIds FROM (((Course LEFT JOIN (SELECT courseId,GROUP_CONCAT(prereqId) prereqIds FROM PreReq GROUP BY courseId) p USING(courseId)) INNER JOIN Classroom ON Course.classroomId=Classroom.classroomId) INNER JOIN Instructor ON Course.username = Instructor.username) WHERE Classroom.name=campusname AND Course.credits<=maxCredits AND Course.credits>=minCredits AND Instructor.departmentId=xdepartmentId;
  END;
  """)


cursor.execute("""DROP PROCEDURE IF EXISTS FilterWithKeyword;""")
connection.commit()

cursor.execute("""
  CREATE PROCEDURE FilterWithKeyword(IN keyword CHAR(40),IN xdepartmentId CHAR(10),IN campusname CHAR(20), IN minCredits INTEGER, IN maxCredits INTEGER)
  BEGIN
    SELECT Course.courseId, Course.name, Instructor.surname, Instructor.departmentId, credits, Course.classroomId, Course.slotNumber, Course.quota, prereqIds FROM (((Course LEFT JOIN (SELECT courseId,GROUP_CONCAT(prereqId) prereqIds FROM PreReq GROUP BY courseId) p USING(courseId)) INNER JOIN Classroom ON Course.classroomId=Classroom.classroomId) INNER JOIN Instructor ON Course.username = Instructor.username) WHERE Classroom.name=campusname AND Course.credits<=maxCredits AND Course.credits>=minCredits AND Instructor.departmentId=xdepartmentId AND Course.name LIKE CONCAT('%', keyword , '%');
  END;
  """)

cursor.execute("""DROP PROCEDURE IF EXISTS StAddCourse;""")
connection.commit()

cursor.execute("""
  CREATE PROCEDURE StAddCourse(IN usernameValue CHAR(20),IN courseIdValue CHAR(10))
  BEGIN
    INSERT INTO Grades (username, courseId)
      VALUES
        (
          usernameValue,courseIdValue
        );
  END;
  """)
  



connection.commit()
# connection.commit()

# cursor.execute("INSERT INTO Department (departmentid, name) VALUES ('Cmpe', 'Computer Engineering');")
# cursor.execute("INSERT INTO DatabaseManager (adminname, password) VALUES ('taha', 'pass');")
# # cursor.execute('INSERT INTO User VALUES ("niyazi.ulke","password");')
# # cursor.execute('INSERT INTO Post VALUES ("Post1","Post 1 of berke.argin","berke.argin");')
# # cursor.execute('INSERT INTO Post VALUES ("Post2","Post 2 of berke.argin","berke.argin");')
# # cursor.execute('INSERT INTO Post VALUES ("Post3","Post 3 of berke.argin","berke.argin");')
# connection.commit()
