-- openu-physics-desk schema
SET NAMES utf8mb4;
SET CHARACTER SET utf8mb4;

CREATE TABLE IF NOT EXISTS courses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    course_num  VARCHAR(10)  NOT NULL UNIQUE,
    course_name VARCHAR(150) NOT NULL
);

CREATE TABLE IF NOT EXISTS contacts (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    category    ENUM('books','exams','lecturers','other') NOT NULL,
    course_id   INT DEFAULT NULL,
    message     TEXT NOT NULL,
    email       VARCHAR(100) DEFAULT NULL,
    phone       VARCHAR(20)  DEFAULT NULL,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (course_id) REFERENCES courses(id)
);

CREATE TABLE IF NOT EXISTS announcements (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    title      VARCHAR(150) NOT NULL,
    content    TEXT         NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS meeting_summaries (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    title        VARCHAR(150) DEFAULT NULL,
    content      TEXT NOT NULL,
    meeting_date DATE DEFAULT (CURRENT_DATE),
    created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS admins (
    id            INT AUTO_INCREMENT PRIMARY KEY,
    username      VARCHAR(50)  NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('admin','superadmin') DEFAULT 'admin',
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
