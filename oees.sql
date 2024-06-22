CREATE DATABASE IF NOT EXISTS oees;
USE oees;


CREATE TABLE IF NOT EXISTS `STUDENT` (
  `fname` VARCHAR(20) NOT NULL,
  `lname` VARCHAR(20) NOT NULL,
  `rollnumber` VARCHAR(15) PRIMARY KEY,
  `password` VARCHAR(30) NOT NULL,
  `email` VARCHAR(60) UNIQUE NOT NULL,
  `mob_no` VARCHAR(15) UNIQUE NOT NULL,
  `department` VARCHAR(45) NOT NULL,
  `sem` INT NOT NULL,
  `dob` DATE NULL,
  `guardian` VARCHAR(45) NULL,
  `g_mob_no` VARCHAR(15) NULL,
  `img` MEDIUMBLOB NULL,
  `about` VARCHAR(45) NULL
)ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `FACULTY` (
  `fname` VARCHAR(20) NOT NULL,
  `lname` VARCHAR(20) NOT NULL,
  `rollnumber` VARCHAR(15) PRIMARY KEY,
  `password` VARCHAR(30) NOT NULL,
  `email` VARCHAR(60) UNIQUE NOT NULL,
  `mob_no` VARCHAR(15) UNIQUE NOT NULL,
  `department` VARCHAR(45) NOT NULL,
  `img` MEDIUMBLOB NULL,
  `about` VARCHAR(45) NULL
)ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `QUESTION` (
  `test_id` INT,
  `ques_id` INT,
  `rollnumber` VARCHAR(15) NOT NULL,
  `question` LONGTEXT NOT NULL,
  `q_img` MEDIUMBLOB NULL,
  `opt_A` LONGTEXT NULL,
  `opt_A_img` MEDIUMBLOB NULL,
  `opt_B` LONGTEXT NULL,
  `opt_B_img` MEDIUMBLOB NULL,
  `opt_C` LONGTEXT NULL,
  `opt_C_img` MEDIUMBLOB NULL,
  `opt_D` LONGTEXT NULL,
  `opt_D_img` MEDIUMBLOB NULL,
  `opt_ans` VARCHAR(1) NULL,
  `answer` LONGTEXT NULL,
  `q_marks` INT NOT NULL,
  PRIMARY KEY (`test_id`, `ques_id`),
  INDEX `rollnumber_idx` (`rollnumber` ASC),
  CONSTRAINT `rollnumber`
    FOREIGN KEY (`rollnumber`)
    REFERENCES `FACULTY` (`rollnumber`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `EXAM` (
  `test_id` INT UNIQUE,
  `exam_name` VARCHAR(50),
  `rollnumber` VARCHAR(15) NOT NULL,
  `dept_sem` JSON NOT NULL,
  `start_datetime` DATETIME NOT NULL,
  `end_datetime` DATETIME NOT NULL,
  `img` MEDIUMBLOB NULL,
  PRIMARY KEY (`test_id`, `exam_name`),
  INDEX `rollnumber_idx` (`rollnumber` ASC),
  INDEX `test_id_idx` (`test_id` ASC),
  INDEX `exam_name_idx` (`exam_name` ASC),
  CONSTRAINT `test_id`
    FOREIGN KEY (`test_id`)
    REFERENCES `QUESTION` (`test_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `rollnumber`
    FOREIGN KEY (`rollnumber`)
    REFERENCES `FACULTY` (`rollnumber`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `RESPONSE` (
  `rollnumber` VARCHAR(15) NOT NULL,
  `test_id` INT,
  `ques_id` INT,
  `opt_ans` VARCHAR(1) NULL,
  `answer` LONGTEXT NULL,
  `q_marks` INT NOT NULL,
  PRIMARY KEY (`rollnumber`, `test_id`, `ques_id`),
  INDEX `rollnumber_idx` (`rollnumber` ASC),
  INDEX `test_id_idx` (`test_id` ASC),
  INDEX `ques_id_idx` (`ques_id` ASC),
  CONSTRAINT `rollnumber`
    FOREIGN KEY (`rollnumber`)
    REFERENCES `STUDENT` (`rollnumber`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `test_id`
    FOREIGN KEY (`test_id`)
    REFERENCES `QUESTION` (`test_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `ques_id`
    FOREIGN KEY (`ques_id`)
    REFERENCES `QUESTION` (`ques_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)ENGINE=MyISAM;


CREATE TABLE IF NOT EXISTS `RESULTS` (
  `rollnumber` VARCHAR(15),
  `test_id` INT,
  `marks_obtained` INT(3) NOT NULL,
  `total_marks` INT(3) NOT NULL,
  PRIMARY KEY (`rollnumber`, `test_id`),
  INDEX `rollnumber_idx` (`rollnumber` ASC),
  INDEX `test_id_idx` (`test_id` ASC),
  CONSTRAINT `rollnumber`
    FOREIGN KEY (`rollnumber`)
    REFERENCES `STUDENT` (`rollnumber`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `test_id`
    FOREIGN KEY (`test_id`)
    REFERENCES `RESPONSE` (`test_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION
)ENGINE=MyISAM;