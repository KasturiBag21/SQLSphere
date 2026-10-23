-- SQLSphere student database restoration script
-- This creates ONLY the SQLSphere database: student_management.
-- It does not touch any other MySQL database.

CREATE DATABASE IF NOT EXISTS student_management;
USE student_management;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS marks;
DROP TABLE IF EXISTS enrollments;
DROP TABLE IF EXISTS courses;
DROP TABLE IF EXISTS faculty;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS departments;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE departments (
    department_id INT PRIMARY KEY AUTO_INCREMENT,
    department_name VARCHAR(100) NOT NULL,
    hod_name VARCHAR(100),
    building VARCHAR(100),
    phone VARCHAR(20)
);

CREATE TABLE students (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    student_name VARCHAR(100) NOT NULL,
    gender VARCHAR(20),
    age INT,
    cgpa DECIMAL(4,2),
    department_id INT NOT NULL,
    email VARCHAR(150),
    phone VARCHAR(20),
    year_of_study INT,
    CONSTRAINT fk_students_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE faculty (
    faculty_id INT PRIMARY KEY AUTO_INCREMENT,
    faculty_name VARCHAR(100) NOT NULL,
    designation VARCHAR(100),
    email VARCHAR(150),
    phone VARCHAR(20),
    department_id INT NOT NULL,
    CONSTRAINT fk_faculty_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
);

CREATE TABLE courses (
    course_id INT PRIMARY KEY AUTO_INCREMENT,
    course_name VARCHAR(150) NOT NULL,
    credits INT,
    semester INT,
    department_id INT NOT NULL,
    faculty_id INT,
    CONSTRAINT fk_courses_department
        FOREIGN KEY (department_id) REFERENCES departments(department_id),
    CONSTRAINT fk_courses_faculty
        FOREIGN KEY (faculty_id) REFERENCES faculty(faculty_id)
);

CREATE TABLE enrollments (
    enrollment_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    semester INT,
    CONSTRAINT fk_enrollments_student
        FOREIGN KEY (student_id) REFERENCES students(student_id),
    CONSTRAINT fk_enrollments_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE marks (
    mark_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    mid_sem DECIMAL(5,2),
    end_sem DECIMAL(5,2),
    total DECIMAL(5,2),
    grade VARCHAR(5),
    CONSTRAINT fk_marks_student
        FOREIGN KEY (student_id) REFERENCES students(student_id),
    CONSTRAINT fk_marks_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

CREATE TABLE attendance (
    attendance_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    attendance_percentage DECIMAL(5,2),
    CONSTRAINT fk_attendance_student
        FOREIGN KEY (student_id) REFERENCES students(student_id),
    CONSTRAINT fk_attendance_course
        FOREIGN KEY (course_id) REFERENCES courses(course_id)
);

-- Departments
INSERT INTO departments (department_name, hod_name, building, phone) VALUES
('Computer Science and Engineering', 'Dr. Anil Kumar', 'Block A', '9876500001'),
('Information Technology', 'Dr. Priya Sharma', 'Block B', '9876500002'),
('Electronics and Communication Engineering', 'Dr. Rajesh Menon', 'Block C', '9876500003'),
('Mechanical Engineering', 'Dr. Suresh Rao', 'Block D', '9876500004'),
('Electrical and Electronics Engineering', 'Dr. Meena Iyer', 'Block E', '9876500005');

-- Students
INSERT INTO students
(student_name, gender, age, cgpa, department_id, email, phone, year_of_study)
VALUES
('Aarav Sharma','Male',20,8.72,1,'aarav.sharma@example.com','9000000001',3),
('Ananya Patel','Female',21,9.10,1,'ananya.patel@example.com','9000000002',4),
('Rohan Das','Male',19,7.85,1,'rohan.das@example.com','9000000003',2),
('Sneha Nair','Female',20,8.45,1,'sneha.nair@example.com','9000000004',3),
('Vikram Singh','Male',21,7.92,2,'vikram.singh@example.com','9000000005',4),
('Ishita Roy','Female',20,9.25,2,'ishita.roy@example.com','9000000006',3),
('Karan Mehta','Male',19,8.05,2,'karan.mehta@example.com','9000000007',2),
('Neha Gupta','Female',21,8.68,2,'neha.gupta@example.com','9000000008',4),
('Arjun Menon','Male',20,8.34,3,'arjun.menon@example.com','9000000009',3),
('Diya Shah','Female',19,9.02,3,'diya.shah@example.com','9000000010',2),
('Rahul Verma','Male',21,7.76,3,'rahul.verma@example.com','9000000011',4),
('Pooja Iyer','Female',20,8.81,3,'pooja.iyer@example.com','9000000012',3),
('Aditya Rao','Male',22,8.15,4,'aditya.rao@example.com','9000000013',4),
('Meera Joshi','Female',20,9.18,4,'meera.joshi@example.com','9000000014',3),
('Nikhil Kumar','Male',19,7.64,4,'nikhil.kumar@example.com','9000000015',2),
('Kavya Reddy','Female',21,8.52,4,'kavya.reddy@example.com','9000000016',4),
('Sanjay Das','Male',20,8.40,5,'sanjay.das@example.com','9000000017',3),
('Aditi Bose','Female',19,9.05,5,'aditi.bose@example.com','9000000018',2),
('Manish Jain','Male',21,7.98,5,'manish.jain@example.com','9000000019',4),
('Riya Kapoor','Female',20,8.74,5,'riya.kapoor@example.com','9000000020',3);

-- Faculty
INSERT INTO faculty
(faculty_name, designation, email, phone, department_id)
VALUES
('Dr. Anil Kumar','Professor','anil.kumar@example.com','9100000001',1),
('Dr. Kavita Rao','Associate Professor','kavita.rao@example.com','9100000002',1),
('Dr. Priya Sharma','Professor','priya.sharma@example.com','9100000003',2),
('Dr. Amit Verma','Assistant Professor','amit.verma@example.com','9100000004',2),
('Dr. Rajesh Menon','Professor','rajesh.menon@example.com','9100000005',3),
('Dr. Lakshmi Nair','Associate Professor','lakshmi.nair@example.com','9100000006',3),
('Dr. Suresh Rao','Professor','suresh.rao@example.com','9100000007',4),
('Dr. Meena Iyer','Professor','meena.iyer@example.com','9100000008',5);

-- Courses
INSERT INTO courses
(course_name, credits, semester, department_id, faculty_id)
VALUES
('Database Management Systems',4,5,1,1),
('Artificial Intelligence',4,6,1,2),
('Computer Networks',3,5,1,1),
('Web Technologies',3,5,2,3),
('Data Analytics',4,6,2,4),
('Digital Electronics',4,5,3,5),
('Communication Systems',3,6,3,6),
('Thermodynamics',4,5,4,7),
('Electrical Machines',4,5,5,8),
('Power Systems',3,6,5,8);

-- Enrollments: each student is enrolled in two courses from their department.
INSERT INTO enrollments (student_id, course_id, semester) VALUES
(1,1,5),(1,2,6),
(2,1,5),(2,2,6),
(3,1,5),(3,3,5),
(4,1,5),(4,3,5),
(5,4,5),(5,5,6),
(6,4,5),(6,5,6),
(7,4,5),(7,5,6),
(8,4,5),(8,5,6),
(9,6,5),(9,7,6),
(10,6,5),(10,7,6),
(11,6,5),(11,7,6),
(12,6,5),(12,7,6),
(13,8,5),(13,8,5),
(14,8,5),(14,8,5),
(15,8,5),(15,8,5),
(16,8,5),(16,8,5),
(17,9,5),(17,10,6),
(18,9,5),(18,10,6),
(19,9,5),(19,10,6),
(20,9,5),(20,10,6);

-- Marks for the first course of each student.
INSERT INTO marks (student_id, course_id, mid_sem, end_sem, total, grade) VALUES
(1,1,24,58,82,'A'),(2,1,27,62,89,'A+'),(3,1,20,51,71,'B+'),(4,1,23,56,79,'A'),
(5,4,25,57,82,'A'),(6,4,28,64,92,'A+'),(7,4,21,50,71,'B+'),(8,4,26,59,85,'A'),
(9,6,22,55,77,'A'),(10,6,27,61,88,'A+'),(11,6,19,48,67,'B'),(12,6,25,58,83,'A'),
(13,8,21,53,74,'B+'),(14,8,28,63,91,'A+'),(15,8,18,47,65,'B'),(16,8,24,56,80,'A'),
(17,9,23,55,78,'A'),(18,9,27,63,90,'A+'),(19,9,20,51,71,'B+'),(20,9,26,59,85,'A');

-- Marks for the second course where applicable.
INSERT INTO marks (student_id, course_id, mid_sem, end_sem, total, grade) VALUES
(1,2,22,54,76,'A'),(2,2,29,64,93,'A+'),(3,3,21,49,70,'B+'),(4,3,24,55,79,'A'),
(5,5,23,56,79,'A'),(6,5,28,63,91,'A+'),(7,5,20,52,72,'B+'),(8,5,25,58,83,'A'),
(9,7,23,54,77,'A'),(10,7,28,62,90,'A+'),(11,7,18,47,65,'B'),(12,7,26,57,83,'A'),
(13,8,22,50,72,'B+'),(14,8,27,62,89,'A+'),(15,8,19,45,64,'B'),(16,8,25,55,80,'A'),
(17,10,24,56,80,'A'),(18,10,29,63,92,'A+'),(19,10,21,50,71,'B+'),(20,10,27,59,86,'A');

-- Attendance
INSERT INTO attendance (student_id, course_id, attendance_percentage) VALUES
(1,1,91),(1,2,88),(2,1,96),(2,2,94),(3,1,82),(3,3,85),(4,1,89),(4,3,91),
(5,4,87),(5,5,90),(6,4,97),(6,5,95),(7,4,81),(7,5,84),(8,4,92),(8,5,93),
(9,6,88),(9,7,90),(10,6,96),(10,7,95),(11,6,79),(11,7,82),(12,6,91),(12,7,89),
(13,8,86),(14,8,94),(15,8,78),(16,8,90),
(17,9,92),(17,10,88),(18,9,97),(18,10,96),(19,9,83),(19,10,85),(20,9,91),(20,10,93);

-- Quick verification
SELECT 'departments' AS table_name, COUNT(*) AS row_count FROM departments
UNION ALL SELECT 'students', COUNT(*) FROM students
UNION ALL SELECT 'faculty', COUNT(*) FROM faculty
UNION ALL SELECT 'courses', COUNT(*) FROM courses
UNION ALL SELECT 'enrollments', COUNT(*) FROM enrollments
UNION ALL SELECT 'marks', COUNT(*) FROM marks
UNION ALL SELECT 'attendance', COUNT(*) FROM attendance;
