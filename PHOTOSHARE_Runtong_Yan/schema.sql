DROP DATABASE photoshare;
CREATE DATABASE photoshare;
USE photoshare;

-- CREATE USER TABLE
CREATE TABLE Users (
    UID INT NOT NULL AUTO_INCREMENT,
	  email VARCHAR(40) UNIQUE,
    password VARCHAR(40) NOT NULL,
	  first_name VARCHAR(40) NOT NULL DEFAULT "Runtong",
    last_name VARCHAR(40) NOT NULL DEFAULT "Yan",
    gender VARCHAR(6),
    dob VARCHAR(10),
    hometown VARCHAR(40),
		contribution INT,
    CONSTRAINT user_pk PRIMARY KEY (UID)
);

-- CREATE FRIENDSHIP TABLE
CREATE TABLE FRIENDSHIP(
	UID1 INT NOT NULL,
	UID2 INT NOT NULL,
	PRIMARY KEY(UID1, UID2),
	FOREIGN KEY (UID1) REFERENCES Users(UID) ON DELETE CASCADE,
	FOREIGN KEY (UID2) REFERENCES Users(UID) ON DELETE CASCADE
);


-- CREATE Album TABLE (include album entity and 'own' relationship)
CREATE TABLE ALBUM(
	AID INT NOT NULL AUTO_INCREMENT,
	NAME VARCHAR(40) NOT NULL,
	DOC TIMESTAMP NOT NULL,
	UID INT NOT NULL,
	PRIMARY KEY (AID),
	FOREIGN KEY (UID) REFERENCES Users(UID) ON DELETE CASCADE
);

-- CREATE Photo TABLE (include photo entity and 'contains' relationship)
CREATE TABLE PHOTO(
	PID INT NOT NULL AUTO_INCREMENT,
	CAPTION VARCHAR(200),
	DATA LONGBLOB NOT NULL,
	UID INT NOT NULL,
	AID INT NOT NULL,
	PRIMARY KEY (PID),
	FOREIGN KEY (UID) REFERENCES Users(UID) ON DELETE CASCADE,
	FOREIGN KEY (AID) REFERENCES ALBUM(AID) ON DELETE CASCADE
);

-- CREATE Comment TABLE (include comment entity and 'comment' relationship)
CREATE TABLE COMMENT(
	CID INT NOT NULL AUTO_INCREMENT,
	CONTENT VARCHAR(200) NOT NULL,
	DOC TIMESTAMP NOT NULL,
	UID INT,
	PID INT NOT NULL,
	PRIMARY KEY (CID),
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);

-- CREATE THE LIKETABLE. WE CAN'T name it LIKE
CREATE TABLE LIKETABLE(
	UID INT NOT NULL,
	PID INT NOT NULL,
	DOC TIMESTAMP NOT NULL,
  PRIMARY KEY (UID, PID),
	FOREIGN KEY (UID) REFERENCES Users(UID) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);


-- CREATE Tag TABLE
CREATE TABLE TAG(
	HASHTAG VARCHAR(40) NOT NULL,
	PRIMARY KEY (HASHTAG)
);

-- CREATE Associate Table
CREATE TABLE ASSOCIATE(
	PID INT NOT NULL,
	HASHTAG VARCHAR(40) NOT NULL,
  PRIMARY KEY (PID, HASHTAG),
	FOREIGN KEY (HASHTAG) REFERENCES TAG(HASHTAG) ON DELETE CASCADE,
	FOREIGN KEY (PID) REFERENCES PHOTO(PID) ON DELETE CASCADE
);

INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test@bu.edu', 'test', 'yang', 'zhao', 'male', '19970502', 'henan', 0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test1@bu.edu', 'test', 'yuhui', 'fang', 'female', '19970205', 'beijing', 0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test2@bu.edu', 'test', 'zhu', 'zhong', 'male', '19970306', 'beijing', 0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test3@bu.edu', 'test', 'yu', 'fan', 'female', '19970405', 'changsha',0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test4@bu.edu', 'test', 'haowei', 'liu', 'male', '19970505', 'beijing', 0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test5@bu.edu', 'test', 'yuqing', 'zhang', 'male', '19960205', 'zhejiang',0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test6@bu.edu', 'test', 'gua', 'kang', 'male', '19971205', 'beijing',0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test7@bu.edu', 'test', 'chu', 'zhang', 'female', '19990205', 'wuhan',0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test8@bu.edu', 'test', 'runtong', 'yan', 'male', '19950205', 'beijing',0);
INSERT INTO Users (email, password, first_name, last_name, gender, dob, hometown, contribution) VALUES ('test9@bu.edu', 'test', 'tianqi', 'zhao', 'male', '19660205', 'dongbei',0);
