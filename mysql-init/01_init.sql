CREATE SCHEMA IF NOT EXISTS easyabroad;
USE easyabroad;


CREATE TABLE IF NOT EXISTS users (
  id INT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(255),
  last_name VARCHAR(255),
  email VARCHAR(255) UNIQUE,
  password_hash VARCHAR(255),
  role ENUM('student','consultant','admin'),
  city VARCHAR(255),
  country VARCHAR(255),
  birthday DATE,
  gender ENUM('male','female','other'),
  access_level ENUM('standard','super') DEFAULT 'standard',
  profile_picture VARCHAR(255),
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (country_name) REFERENCES countries(country_name)
);


CREATE TABLE IF NOT EXISTS Education (
  user_id INT PRIMARY KEY,
  city_of_study VARCHAR(255),
  country_of_study VARCHAR(255),
  university_name VARCHAR(255),
  course_name VARCHAR(255),
  education_start DATETIME,
  education_finish DATETIME,
  proof_of_education VARCHAR(255),
  accommodation BOOLEAN,
  social_life BOOLEAN,
  uni_info BOOLEAN,
  travel_info BOOLEAN,
  zoom BOOLEAN,
  microsoft_teams BOOLEAN,
  google_meet BOOLEAN,
  apple_facetime BOOLEAN,
  is_verified BOOLEAN,
  verified_by INT,
  verified_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (verified_by) REFERENCES users(id),
  FOREIGN KEY (country_of_study) REFERENCES countries(country_name)
);


CREATE TABLE IF NOT EXISTS Internship (
  user_id INT PRIMARY KEY,
  city_of_internship VARCHAR(255),
  country_of_internship VARCHAR(255),
  company_name VARCHAR(255),
  department_name VARCHAR(255),
  internship_start DATETIME,
  internship_finish DATETIME,
  proof_of_internship VARCHAR(255),
  accommodation BOOLEAN,
  social_life BOOLEAN,
  company_info BOOLEAN,
  travel_info BOOLEAN,
  zoom BOOLEAN,
  microsoft_teams BOOLEAN,
  google_meet BOOLEAN,
  apple_facetime BOOLEAN,
  is_verified BOOLEAN,
  verified_by INT,
  verified_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (verified_by) REFERENCES users(id),
  FOREIGN KEY (country_of_internship) REFERENCES countries(country_name)
);


CREATE TABLE IF NOT EXISTS languages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  language_code VARCHAR(10) UNIQUE,
  language_name VARCHAR(100)        
);

CREATE TABLE IF NOT EXISTS user_languages (
  user_id INT,
  language_id INT,
  PRIMARY KEY (user_id, language_id),
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (language_id) REFERENCES languages(id)
);


INSERT INTO languages (language_code, language_name) VALUES
('af', 'Afrikaans'),
('sq', 'Albanian'),
('am', 'Amharic'),
('ar', 'Arabic'),
('hy', 'Armenian'),
('az', 'Azerbaijani'),
('eu', 'Basque'),
('be', 'Belarusian'),
('bn', 'Bengali'),
('bs', 'Bosnian'),
('bg', 'Bulgarian'),
('ca', 'Catalan'),
('ceb', 'Cebuano'),
('ny', 'Chichewa'),
('zh', 'Chinese (Mandarin)'),
('co', 'Corsican'),
('hr', 'Croatian'),
('cs', 'Czech'),
('da', 'Danish'),
('nl', 'Dutch'),
('en', 'English'),
('eo', 'Esperanto'),
('et', 'Estonian'),
('tl', 'Filipino'),
('fi', 'Finnish'),
('fr', 'French'),
('fy', 'Frisian'),
('gl', 'Galician'),
('ka', 'Georgian'),
('de', 'German'),
('el', 'Greek'),
('gu', 'Gujarati'),
('ht', 'Haitian Creole'),
('ha', 'Hausa'),
('haw', 'Hawaiian'),
('iw', 'Hebrew'),
('hi', 'Hindi'),
('hmn', 'Hmong'),
('hu', 'Hungarian'),
('is', 'Icelandic'),
('ig', 'Igbo'),
('id', 'Indonesian'),
('ga', 'Irish'),
('it', 'Italian'),
('ja', 'Japanese'),
('jw', 'Javanese'),
('kn', 'Kannada'),
('kk', 'Kazakh'),
('km', 'Khmer'),
('rw', 'Kinyarwanda'),
('ko', 'Korean'),
('ku', 'Kurdish (Kurmanji)'),
('ky', 'Kyrgyz'),
('lo', 'Lao'),
('la', 'Latin'),
('lv', 'Latvian'),
('lt', 'Lithuanian'),
('lb', 'Luxembourgish'),
('mk', 'Macedonian'),
('mg', 'Malagasy'),
('ms', 'Malay'),
('ml', 'Malayalam'),
('mt', 'Maltese'),
('mi', 'Maori'),
('mr', 'Marathi'),
('mn', 'Mongolian'),
('my', 'Myanmar (Burmese)'),
('ne', 'Nepali'),
('no', 'Norwegian'),
('or', 'Odia'),
('ps', 'Pashto'),
('fa', 'Persian'),
('pl', 'Polish'),
('pt', 'Portuguese'),
('pa', 'Punjabi'),
('ro', 'Romanian'),
('ru', 'Russian'),
('sm', 'Samoan'),
('gd', 'Scots Gaelic'),
('sr', 'Serbian'),
('st', 'Sesotho'),
('sn', 'Shona'),
('sd', 'Sindhi'),
('si', 'Sinhala'),
('sk', 'Slovak'),
('sl', 'Slovenian'),
('so', 'Somali'),
('es', 'Spanish'),
('su', 'Sundanese'),
('sw', 'Swahili'),
('sv', 'Swedish'),
('tg', 'Tajik'),
('ta', 'Tamil'),
('tt', 'Tatar'),
('te', 'Telugu'),
('th', 'Thai'),
('tr', 'Turkish'),
('tk', 'Turkmen'),
('uk', 'Ukrainian'),
('ur', 'Urdu'),
('ug', 'Uyghur'),
('uz', 'Uzbek'),
('vi', 'Vietnamese'),
('cy', 'Welsh'),
('xh', 'Xhosa'),
('yi', 'Yiddish'),
('yo', 'Yoruba'),
('zu', 'Zulu');


CREATE TABLE IF NOT EXISTS Calendar (
  user_id INT,
  available_day ENUM('Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'),
  available_time_start TIME,
  available_time_end TIME,
  PRIMARY KEY (user_id, available_day, available_time_start),
  FOREIGN KEY (user_id) REFERENCES users(id)
);


CREATE TABLE IF NOT EXISTS bookings (
  id INT PRIMARY KEY AUTO_INCREMENT,
  student_id INT,
  consultant_id INT,
  status ENUM('pending', 'confirmed', 'cancelled', 'completed') DEFAULT 'pending',
  booked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  scheduled_start DATETIME,
  scheduled_end DATETIME,
  reason ENUM('accommodation', 'social_life', 'uni_info', 'travel_info', 'company_info'),
  platform ENUM('zoom', 'microsoft_teams', 'google_meet', 'apple_facetime'),
  FOREIGN KEY (student_id) REFERENCES users(id),
  FOREIGN KEY (consultant_id) REFERENCES users(id)
);


UPDATE bookings
SET status = 'completed'
WHERE status = 'confirmed' AND scheduled_end < NOW();


CREATE TABLE IF NOT EXISTS sessions (
  id INT PRIMARY KEY AUTO_INCREMENT,
  booking_id INT UNIQUE,  -- one session per booking
  video_link VARCHAR(255),
  started_at DATETIME,
  ended_at DATETIME,
  pre_session_notes TEXT,
  post_session_notes TEXT,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  FOREIGN KEY (booking_id) REFERENCES bookings(id)
);


-- Messages table
CREATE TABLE IF NOT EXISTS messages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  sender_id INT NOT NULL,
  receiver_id INT NOT NULL,
  booking_id INT,
  encrypted_message VARBINARY(512) NOT NULL,
  encryption_iv VARBINARY(16) NOT NULL,
  is_reported BOOLEAN DEFAULT FALSE,
  reported_at DATETIME,
  sent_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at DATETIME DEFAULT (CURRENT_TIMESTAMP + INTERVAL 3 YEAR),
  FOREIGN KEY (sender_id) REFERENCES users(id),
  FOREIGN KEY (receiver_id) REFERENCES users(id),
  FOREIGN KEY (booking_id) REFERENCES bookings(id),
  INDEX (booking_id),
  INDEX (sender_id, receiver_id),
  INDEX (sent_at),
  INDEX (expires_at)
);


-- Remove expired messages
DELETE FROM messages
WHERE expires_at < NOW();


CREATE TABLE IF NOT EXISTS support_tickets (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  subject VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  status ENUM('open','in_progress','resolved','closed') NOT NULL DEFAULT 'open',
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  resolved_by INT,
  resolved_at DATETIME,
  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (resolved_by) REFERENCES users(id),
  INDEX (user_id),
  INDEX (status)
);


CREATE TABLE IF NOT EXISTS uploaded_documents (
  id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT NOT NULL,
  document_name VARCHAR(255) NOT NULL,
  document_type ENUM('company', 'school') NOT NULL,
  upload_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  verification_date DATETIME,
  is_valid BOOLEAN DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES users(id),
  INDEX (user_id),
  INDEX (is_valid)
);


DELIMITER $$


CREATE TRIGGER trg_after_document_verify
AFTER UPDATE ON uploaded_documents
FOR EACH ROW
BEGIN
  -- Check if document was just verified
  IF OLD.is_valid = FALSE AND NEW.is_valid = TRUE THEN
    -- Delete the record from table after verification
    DELETE FROM uploaded_documents WHERE id = NEW.id;
    -- Note: This will cause recursion if not handled properly; better handled in backend!
  END IF;
END $$


DELIMITER ;


CREATE TABLE IF NOT EXISTS contact_messages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) NOT NULL,
  message TEXT NOT NULL,
  submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS countries (
  id INT PRIMARY KEY AUTO_INCREMENT,
  country_name VARCHAR(255) NOT NULL UNIQUE,
  country_code CHAR(2) NOT NULL UNIQUE
);


INSERT INTO countries (country_name, country_code) VALUES
('Afghanistan', 'AF'),
('Albania', 'AL'),
('Algeria', 'DZ'),
('Andorra', 'AD'),
('Angola', 'AO'),
('Argentina', 'AR'),
('Armenia', 'AM'),
('Australia', 'AU'),
('Austria', 'AT'),
('Azerbaijan', 'AZ'),
('Bahamas', 'BS'),
('Bahrain', 'BH'),
('Bangladesh', 'BD'),
('Barbados', 'BB'),
('Belarus', 'BY'),
('Belgium', 'BE'),
('Belize', 'BZ'),
('Benin', 'BJ'),
('Bhutan', 'BT'),
('Bolivia', 'BO'),
('Bosnia and Herzegovina', 'BA'),
('Botswana', 'BW'),
('Brazil', 'BR'),
('Brunei', 'BN'),
('Bulgaria', 'BG'),
('Burkina Faso', 'BF'),
('Burundi', 'BI'),
('Cabo Verde', 'CV'),
('Cambodia', 'KH'),
('Cameroon', 'CM'),
('Canada', 'CA'),
('Central African Republic', 'CF'),
('Chad', 'TD'),
('Chile', 'CL'),
('China', 'CN'),
('Colombia', 'CO'),
('Comoros', 'KM'),
('Congo', 'CG'),
('Costa Rica', 'CR'),
('Croatia', 'HR'),
('Cuba', 'CU'),
('Cyprus', 'CY'),
('Czechia', 'CZ'),
('Democratic Republic of the Congo', 'CD'),
('Denmark', 'DK'),
('Djibouti', 'DJ'),
('Dominica', 'DM'),
('Dominican Republic', 'DO'),
('Ecuador', 'EC'),
('Egypt', 'EG'),
('El Salvador', 'SV'),
('Equatorial Guinea', 'GQ'),
('Eritrea', 'ER'),
('Estonia', 'EE'),
('Eswatini', 'SZ'),
('Ethiopia', 'ET'),
('Fiji', 'FJ'),
('Finland', 'FI'),
('France', 'FR'),
('Gabon', 'GA'),
('Gambia', 'GM'),
('Georgia', 'GE'),
('Germany', 'DE'),
('Ghana', 'GH'),
('Greece', 'GR'),
('Grenada', 'GD'),
('Guatemala', 'GT'),
('Guinea', 'GN'),
('Guinea-Bissau', 'GW'),
('Guyana', 'GY'),
('Haiti', 'HT'),
('Holy See', 'VA'),
('Honduras', 'HN'),
('Hungary', 'HU'),
('Iceland', 'IS'),
('India', 'IN'),
('Indonesia', 'ID'),
('Iran', 'IR'),
('Iraq', 'IQ'),
('Ireland', 'IE'),
('Israel', 'IL'),
('Italy', 'IT'),
('Jamaica', 'JM'),
('Japan', 'JP'),
('Jordan', 'JO'),
('Kazakhstan', 'KZ'),
('Kenya', 'KE'),
('Kiribati', 'KI'),
('Kuwait', 'KW'),
('Kyrgyzstan', 'KG'),
('Laos', 'LA'),
('Latvia', 'LV'),
('Lebanon', 'LB'),
('Lesotho', 'LS'),
('Liberia', 'LR'),
('Libya', 'LY'),
('Liechtenstein', 'LI'),
('Lithuania', 'LT'),
('Luxembourg', 'LU'),
('Madagascar', 'MG'),
('Malawi', 'MW'),
('Malaysia', 'MY'),
('Maldives', 'MV'),
('Mali', 'ML'),
('Malta', 'MT'),
('Marshall Islands', 'MH'),
('Mauritania', 'MR'),
('Mauritius', 'MU'),
('Mexico', 'MX'),
('Micronesia', 'FM'),
('Moldova', 'MD'),
('Monaco', 'MC'),
('Mongolia', 'MN'),
('Montenegro', 'ME'),
('Morocco', 'MA'),
('Mozambique', 'MZ'),
('Myanmar', 'MM'),
('Namibia', 'NA'),
('Nauru', 'NR'),
('Nepal', 'NP'),
('Netherlands', 'NL'),
('New Zealand', 'NZ'),
('Nicaragua', 'NI'),
('Niger', 'NE'),
('Nigeria', 'NG'),
('North Korea', 'KP'),
('North Macedonia', 'MK'),
('Norway', 'NO'),
('Oman', 'OM'),
('Pakistan', 'PK'),
('Palau', 'PW'),
('Palestine State', 'PS'),
('Panama', 'PA'),
('Papua New Guinea', 'PG'),
('Paraguay', 'PY'),
('Peru', 'PE'),
('Philippines', 'PH'),
('Poland', 'PL'),
('Portugal', 'PT'),
('Qatar', 'QA'),
('Romania', 'RO'),
('Russia', 'RU'),
('Rwanda', 'RW'),
('Saint Kitts and Nevis', 'KN'),
('Saint Lucia', 'LC'),
('Saint Vincent and the Grenadines', 'VC'),
('Samoa', 'WS'),
('San Marino', 'SM'),
('Sao Tome and Principe', 'ST'),
('Saudi Arabia', 'SA'),
('Senegal', 'SN'),
('Serbia', 'RS'),
('Seychelles', 'SC'),
('Sierra Leone', 'SL'),
('Singapore', 'SG'),
('Slovakia', 'SK'),
('Slovenia', 'SI'),
('Solomon Islands', 'SB'),
('Somalia', 'SO'),
('South Africa', 'ZA'),
('South Korea', 'KR'),
('South Sudan', 'SS'),
('Spain', 'ES'),
('Sri Lanka', 'LK'),
('Sudan', 'SD'),
('Suriname', 'SR'),
('Sweden', 'SE'),
('Switzerland', 'CH'),
('Syria', 'SY'),
('Tajikistan', 'TJ'),
('Tanzania', 'TZ'),
('Thailand', 'TH'),
('Timor-Leste', 'TL'),
('Togo', 'TG'),
('Tonga', 'TO'),
('Trinidad and Tobago', 'TT'),
('Tunisia', 'TN'),
('Turkey', 'TR'),
('Turkmenistan', 'TM'),
('Tuvalu', 'TV'),
('Uganda', 'UG'),
('Ukraine', 'UA'),
('United Arab Emirates', 'AE'),
('United Kingdom', 'GB'),
('United States of America', 'US'),
('Uruguay', 'UY'),
('Uzbekistan', 'UZ'),
('Vanuatu', 'VU'),
('Venezuela', 'VE'),
('Vietnam', 'VN'),
('Yemen', 'YE'),
('Zambia', 'ZM'),
('Zimbabwe', 'ZW');


CREATE TABLE refresh_tokens (
  id          BIGINT AUTO_INCREMENT PRIMARY KEY,
  token       VARCHAR(64) NOT NULL UNIQUE,
  user_id     BIGINT NOT NULL,
  issued_at   DATETIME NOT NULL,
  expires_at  DATETIME NOT NULL,
  revoked     BOOLEAN NOT NULL DEFAULT FALSE,
  FOREIGN KEY (user_id) REFERENCES users(id)
);



– Seed Data for Testing Purposes:
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
