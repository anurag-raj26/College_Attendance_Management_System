
CREATE DATABASE IF NOT EXISTS college_attendance;

USE college_attendance;

CREATE TABLE IF NOT EXISTS students (
    roll VARCHAR(30) PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    course VARCHAR(100) NOT NULL
) ENGINE=InnoDB;

CREATE TABLE IF NOT EXISTS attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    att_date DATE NOT NULL,
    subject VARCHAR(100) NOT NULL,
    roll VARCHAR(30) NOT NULL,
    status ENUM('P', 'A') NOT NULL,
    UNIQUE KEY one_per_class (att_date, subject, roll),
    CONSTRAINT fk_attendance_student
        FOREIGN KEY (roll)
        REFERENCES students(roll)
        ON DELETE CASCADE
) ENGINE=InnoDB;

CREATE USER IF NOT EXISTS 'attendance_app'@'localhost'
IDENTIFIED BY 'ChooseYourOwnStrongPassword';

ALTER USER 'attendance_app'@'localhost'
IDENTIFIED BY 'MyNewPrivatePass_2026!';

GRANT SELECT, INSERT, UPDATE, DELETE
ON college_attendance.*
TO 'attendance_app'@'localhost';
