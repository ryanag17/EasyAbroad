USE easyabroad;

-- Countries
INSERT INTO countries (country_name) VALUES
('United States'),
('Germany'),
('France'),
('Japan'),
('Brazil');

-- Users (explicit ids)
INSERT INTO users (id, first_name, last_name, email, password_hash, role, city, country, birthday, gender, access_level, profile_picture)
VALUES
(1, 'Alice', 'Student', 'alice@student.com', 'hashed_password_1', 'student', 'New York', 'United States', '2000-01-01', 'female', 'standard', 'alice.jpg'),
(2, 'Bob', 'Student', 'bob@student.com', 'hashed_password_2', 'student', 'Berlin', 'Germany', '1999-02-02', 'male', 'standard', 'bob.jpg'),
(3, 'Carol', 'Consultant', 'carol@consult.com', 'hashed_password_3', 'consultant', 'Paris', 'France', '1995-03-03', 'female', 'standard', 'carol.jpg'),
(4, 'Dave', 'Consultant', 'dave@consult.com', 'hashed_password_4', 'consultant', 'Tokyo', 'Japan', '1993-04-04', 'male', 'standard', 'dave.jpg'),
(5, 'Eve', 'Admin', 'eve@admin.com', 'hashed_password_5', 'admin', 'San Francisco', 'United States', '1985-05-05', 'female', 'super', 'eve.jpg'),
(6, 'Frank', 'Admin', 'frank@admin.com', 'hashed_password_6', 'admin', 'São Paulo', 'Brazil', '1980-06-06', 'male', 'super', 'frank.jpg');

-- Education (for Carol, user_id 3)
INSERT INTO education (user_id, city_of_study, country_of_study, university_name, course_name, education_start, education_finish, proof_of_education, accommodation, social_life, uni_info, travel_info, zoom, microsoft_teams, google_meet, apple_facetime, is_verified, verified_by, verified_at)
VALUES
(3, 'Paris', 'France', 'Sorbonne University', 'International Relations', '2015-09-01', '2018-06-30', 'sorbonne_proof.pdf', TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, TRUE, 5, NOW());

-- Internship (for Dave, user_id 4)
INSERT INTO internship (user_id, company_name, position, internship_start, internship_end, proof_of_internship, accommodation, social_life, company_info, travel_info, zoom, microsoft_teams, google_meet, apple_facetime, is_verified, verified_by, verified_at)
VALUES
(4, 'Sony Corporation', 'Software Engineer Intern', '2016-07-01', '2017-12-31', 'sony_proof.pdf', FALSE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, TRUE, TRUE, 6, NOW());

-- Calendar (availability for consultants)
INSERT INTO calendar (user_id, available_day, available_time_start, available_time_end)
VALUES
(3, 'Monday', '09:00:00', '17:00:00'),
(4, 'Tuesday', '10:00:00', '18:00:00');

-- Bookings
INSERT INTO bookings (id, student_id, consultant_id, status, booked_at, scheduled_time, start_time, end_time, reason, platform)
VALUES
(1, 1, 3, 'confirmed', NOW(), '2025-06-05 10:00:00', '10:00:00', '11:00:00', 'uni_info', 'zoom'),
(2, 2, 4, 'confirmed', NOW(), '2025-06-06 11:00:00', '11:00:00', '12:00:00', 'company_info', 'google_meet');

-- Sessions
INSERT INTO sessions (booking_id, video_link, started_at, ended_at, notes)
VALUES
(1, 'https://zoom.us/meeting/abc123', '2025-06-05 10:00:00', '2025-06-05 11:00:00', 'Great discussion on study abroad.'),
(2, 'https://meet.google.com/def456', '2025-06-06 11:00:00', '2025-06-06 12:00:00', 'Helpful advice about the internship.');

-- Messages (with dummy hash for encrypted message)
INSERT INTO messages (sender_id, receiver_id, booking_id, message_hash, sent_at)
VALUES
(1, 3, 1, 'hash1', NOW()),
(2, 4, 2, 'hash2', NOW());

-- Uploaded Documents
INSERT INTO uploaded_documents (user_id, document_name, document_type, upload_date, verification_date, is_valid)
VALUES
(3, 'sorbonne_proof.pdf', 'school', NOW(), NOW(), TRUE),
(4, 'sony_proof.pdf', 'company', NOW(), NOW(), TRUE);

-- Support Tickets
INSERT INTO support_tickets (user_id, subject, description, status, created_at, updated_at, resolved_by, resolved_at)
VALUES
(1, 'Account Issue', 'I cannot update my profile.', 'resolved', NOW(), NOW(), 5, NOW()),
(2, 'Booking Problem', 'My consultant didn’t show up.', 'in_progress', NOW(), NOW(), NULL, NULL);

-- Refresh Tokens
INSERT INTO refresh_tokens (token, user_id, issued_at, expires_at, revoked)
VALUES
('token_string_1', 1, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), FALSE),
('token_string_2', 2, NOW(), DATE_ADD(NOW(), INTERVAL 7 DAY), FALSE);

-- Contact Us
INSERT INTO contact_us (name, email, message, submitted_at)
VALUES
('Visitor One', 'visitor1@example.com', 'I have a question about your services.', NOW()),
('Visitor Two', 'visitor2@example.com', 'Can I become a consultant?', NOW());
