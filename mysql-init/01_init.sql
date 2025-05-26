-- backend/database/init.sql

CREATE SCHEMA IF NOT EXISTS easyabroad;
USE easyabroad;

-- Users table now includes reset_token & token_expiry
CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  reset_token     VARCHAR(255)  NULL,
  token_expiry    DATETIME      NULL,
  role ENUM('student','consultant','admin'),
  city VARCHAR(255),
  country VARCHAR(255),
  created_at DATETIME,
  updated_at DATETIME
);

CREATE TABLE IF NOT EXISTS consultants (
  user_id INT PRIMARY KEY,
  birthday DATE,
  gender ENUM('male','female','other'),
  focus ENUM('study','intern','both'),
  languages TEXT,
  place_of_work VARCHAR(255),
  proof_of_education VARCHAR(255),
  education_period DATETIME,
  proof_of_work VARCHAR(255),
  internship_period DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS students (
  user_id INT PRIMARY KEY,
  birthday DATE,
  gender ENUM('male','female','other'),
  languages TINYTEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS admins (
  user_id INT PRIMARY KEY,
  access_level ENUM('standard','super') DEFAULT 'standard',
  notes TEXT,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS Education (
  user_id INT PRIMARY KEY,
  city_of_study VARCHAR(255),
  country_of_study VARCHAR(255),
  university_name VARCHAR(255),
  study_program VARCHAR(255),
  education_start DATETIME,
  education_finish DATETIME,
  proof_of_education VARCHAR(255),
  accommodation BOOLEAN,
  social_life BOOLEAN,
  uni_info BOOLEAN,
  travel_info BOOLEAN,
  is_verified BOOLEAN,
  verified_by INT,
  verified_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES consultants(user_id),
  FOREIGN KEY (verified_by) REFERENCES admins(user_id)
);

CREATE TABLE IF NOT EXISTS Internship (
  user_id INT PRIMARY KEY,
  city_of_internship VARCHAR(255),
  country_of_internship VARCHAR(255),
  company_name VARCHAR(255),
  internship_position VARCHAR(255),
  proof_of_internship VARCHAR(255),
  accommodation BOOLEAN,
  social_life BOOLEAN,
  company_info BOOLEAN,
  travel_info BOOLEAN,
  is_verified BOOLEAN,
  verified_by INT,
  verified_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES consultants(user_id),
  FOREIGN KEY (verified_by) REFERENCES admins(user_id)
);

CREATE TABLE IF NOT EXISTS Calendar (
  user_id INT PRIMARY KEY,
  available_day VARCHAR(255),
  available_time_start TIME,
  available_time_end TIME,
  FOREIGN KEY (user_id) REFERENCES consultants(user_id)
);

CREATE TABLE IF NOT EXISTS bookings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT,
  consultant_id INT,
  status ENUM('pending','confirmed','cancelled','completed'),
  booked_at DATETIME,
  scheduled_time DATETIME,
  duration_minutes INT,
  FOREIGN KEY (student_id) REFERENCES students(user_id),
  FOREIGN KEY (consultant_id) REFERENCES consultants(user_id)
);

CREATE TABLE IF NOT EXISTS sessions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  booking_id INT,
  video_link VARCHAR(255),
  started_at DATETIME,
  ended_at DATETIME,
  notes TEXT,
  FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

CREATE TABLE IF NOT EXISTS messages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sender_id INT,
  receiver_id INT,
  booking_id INT,
  message_text TEXT,
  sent_at DATETIME,
  FOREIGN KEY (sender_id) REFERENCES users(id),
  FOREIGN KEY (receiver_id) REFERENCES users(id),
  FOREIGN KEY (booking_id) REFERENCES bookings(id)
);

CREATE TABLE IF NOT EXISTS support_tickets (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  subject VARCHAR(255),
  description TEXT,
  status ENUM('open','in_progress','resolved','closed'),
  created_at DATETIME,
  updated_at DATETIME,
  resolved_by INT,
  resolved_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (resolved_by) REFERENCES admins(user_id)
);

CREATE TABLE IF NOT EXISTS uploaded_documents (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  document_name VARCHAR(255),
  document_type ENUM('company', 'school'),
  upload_date DATETIME,
  verification_date DATETIME,
  is_valid BOOLEAN,
  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Seed data (admins, consultants, students, etc.) remains unchanged below
USE easyabroad;

-- Insert Admins
INSERT INTO users (first_name, last_name, email, password_hash, role, city, country, created_at, updated_at)
VALUES 
('Alice', 'Admin', 'admin@example.com', 'hashed_pw_admin', 'admin', 'Berlin', 'Germany', NOW(), NOW());

INSERT INTO admins (user_id, access_level, notes)
VALUES (1, 'super', 'Main admin account');

-- Insert Consultants
INSERT INTO users (first_name, last_name, email, password_hash, role, city, country, created_at, updated_at)
VALUES 
('Clara', 'Consultant', 'clara.consult@example.com', 'hashed_pw_consultant', 'consultant', 'Munich', 'Germany', NOW(), NOW());

INSERT INTO consultants (user_id, birthday, gender, focus, languages, place_of_work, proof_of_education, education_period, proof_of_work, internship_period)
VALUES 
(2, '1990-06-15', 'female', 'both', 'English, German', 'StudyHelp GmbH', 'proof_edu.pdf', NOW(), 'proof_work.pdf', NOW());

-- Insert Students
INSERT INTO users (first_name, last_name, email, password_hash, role, city, country, created_at, updated_at)
VALUES 
('Tom', 'Student', 'tom.student@example.com', 'hashed_pw_student', 'student', 'Frankfurt', 'Germany', NOW(), NOW());

INSERT INTO students (user_id, birthday, gender, languages)
VALUES (3, '2002-11-10', 'male', 'English');

-- Seed Calendar for Consultant
INSERT INTO Calendar (user_id, available_day, available_time_start, available_time_end)
VALUES (2, 'Monday', '09:00:00', '12:00:00');

-- Education & Internship Records
INSERT INTO Education (
  user_id, city_of_study, country_of_study, university_name, study_program,
  education_start, education_finish, proof_of_education,
  accommodation, social_life, uni_info, travel_info,
  is_verified, verified_by, verified_at
) VALUES (
  2, 'London', 'UK', 'King\'s College London', 'Business Management',
  '2010-09-01', '2014-06-30', 'proof_kcl.pdf',
  TRUE, TRUE, TRUE, TRUE,
  TRUE, 1, NOW()
);

INSERT INTO Internship (
  user_id, city_of_internship, country_of_internship, company_name, internship_position,
  proof_of_internship, accommodation, social_life, company_info, travel_info,
  is_verified, verified_by, verified_at
) VALUES (
  2, 'Amsterdam', 'Netherlands', 'Heineken', 'Marketing Intern',
  'proof_heineken.pdf', TRUE, TRUE, TRUE, FALSE,
  TRUE, 1, NOW()
);

-- Create Booking
INSERT INTO bookings (student_id, consultant_id, status, booked_at, scheduled_time, duration_minutes)
VALUES (3, 2, 'confirmed', NOW(), DATE_ADD(NOW(), INTERVAL 2 DAY), 60);

-- Create Session
INSERT INTO sessions (booking_id, video_link, started_at, ended_at, notes)
VALUES (1, 'https://zoom.com/session123', NOW(), DATE_ADD(NOW(), INTERVAL 1 HOUR), 'Initial session');

-- Create Message
INSERT INTO messages (sender_id, receiver_id, booking_id, message_text, sent_at)
VALUES (3, 2, 1, 'Looking forward to our session!', NOW());

-- Create Support Ticket
INSERT INTO support_tickets (user_id, subject, description, status, created_at, updated_at, resolved_by, resolved_at)
VALUES (3, 'Password issue', 'I can''t reset my password.', 'resolved', NOW(), NOW(), 1, NOW());

-- Upload Document
INSERT INTO uploaded_documents (user_id, document_name, document_type, upload_date, verification_date, is_valid)
VALUES (2, 'consult_cv.pdf', 'company', NOW(), NOW(), TRUE);
