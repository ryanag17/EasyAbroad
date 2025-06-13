-- ─────────────────────────────────────────────────────────────────────────────
-- 01_init.sql
-- Creates every table (and seeds lookup data) in the correct order. No syntax errors.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1) Create (or switch to) the “easyabroad” schema
-- CREATE SCHEMA IF NOT EXISTS easyabroad;
USE easyabroad;

ALTER USER 'user'@'%' IDENTIFIED WITH mysql_native_password BY 'userpassword';
GRANT ALL PRIVILEGES ON easyabroad.* TO 'user'@'%';
FLUSH PRIVILEGES;

-- 2) COUNTRIES table
--    Must come before any table that references countries(country_name).
CREATE TABLE IF NOT EXISTS countries (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  country_name  VARCHAR(100) NOT NULL UNIQUE,
  country_code  CHAR(2)     NOT NULL UNIQUE
);

-- (Optional) Seed some example countries:
INSERT IGNORE INTO countries (country_name, country_code) VALUES
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


-- 3) USERS table
--    Note: “country_name” must match countries.country_name
CREATE TABLE IF NOT EXISTS users (
  id              INT AUTO_INCREMENT PRIMARY KEY,
  first_name      VARCHAR(255)           NOT NULL,
  last_name       VARCHAR(255)           NOT NULL,
  email           VARCHAR(255) UNIQUE    NOT NULL,
  password_hash   VARCHAR(255)           NOT NULL,
  role            ENUM('student','consultant','admin') NOT NULL,
  city            VARCHAR(255),
  country_name    VARCHAR(100)            NULL,
  birthday        DATE,
  gender          ENUM('male','female','other'),
  access_level    ENUM('standard','super') DEFAULT 'standard',
  profile_picture VARCHAR(255),
  reset_token     VARCHAR(255),
  token_expiry    DATETIME,
  created_at      DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at      DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_users_countries
    FOREIGN KEY (country_name) REFERENCES countries(country_name)
      ON UPDATE CASCADE
      ON DELETE RESTRICT
);


-- 4) EDUCATION table
--    References users(id) and countries(country_name).
CREATE TABLE IF NOT EXISTS Education (
  user_id           INT PRIMARY KEY,
  city_of_study     VARCHAR(255),
  country_of_study  VARCHAR(100),  -- must match countries(country_name)
  university_name   VARCHAR(255),
  course_name       VARCHAR(255),
  education_start   DATETIME,
  education_finish  DATETIME,
  proof_of_education VARCHAR(255),
  submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  accommodation     BOOLEAN,
  social_life       BOOLEAN,
  uni_info          BOOLEAN,
  travel_info       BOOLEAN,
  zoom              BOOLEAN,
  microsoft_teams   BOOLEAN,
  google_meet       BOOLEAN,
  apple_facetime    BOOLEAN,
  verified_by       INT,           -- references users(id)
  verified_at       DATETIME,
  status            VARCHAR(20) NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending', 'accepted', 'rejected')),
  short_note        TEXT,

  CONSTRAINT fk_education_user
    FOREIGN KEY (user_id) REFERENCES users(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,

  CONSTRAINT fk_education_verified_by
    FOREIGN KEY (verified_by) REFERENCES users(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,

  CONSTRAINT fk_education_country
    FOREIGN KEY (country_of_study) REFERENCES countries(country_name)
      ON UPDATE CASCADE
      ON DELETE RESTRICT
);


-- 5) INTERNSHIP table
--    References users(id) and countries(country_name).
CREATE TABLE IF NOT EXISTS Internship (
  user_id               INT PRIMARY KEY,
  city_of_internship    VARCHAR(255),
  country_of_internship VARCHAR(100),  -- must match countries(country_name)
  company_name          VARCHAR(255),
  department_name       VARCHAR(255),
  internship_start      DATETIME,
  internship_finish     DATETIME,
  proof_of_internship   VARCHAR(255),
  submitted_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  accommodation         BOOLEAN,
  social_life           BOOLEAN,
  company_info          BOOLEAN,
  travel_info           BOOLEAN,
  zoom                  BOOLEAN,
  microsoft_teams       BOOLEAN,
  google_meet           BOOLEAN,
  apple_facetime        BOOLEAN,
  verified_by           INT,           -- references users(id)
  verified_at           DATETIME,
  status            VARCHAR(20) NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending', 'accepted', 'rejected')),
  short_note        TEXT,
  
  CONSTRAINT fk_internship_user
    FOREIGN KEY (user_id) REFERENCES users(id)
      ON UPDATE CASCADE
      ON DELETE CASCADE,

  CONSTRAINT fk_internship_verified_by
    FOREIGN KEY (verified_by) REFERENCES users(id)
      ON UPDATE CASCADE
      ON DELETE SET NULL,

  CONSTRAINT fk_internship_country
    FOREIGN KEY (country_of_internship) REFERENCES countries(country_name)
      ON UPDATE CASCADE
      ON DELETE RESTRICT
);


-- 6) LANGUAGES table
--    A lookup table for language codes/names.
CREATE TABLE IF NOT EXISTS languages (
  id            INT PRIMARY KEY AUTO_INCREMENT,
  language_code VARCHAR(10) UNIQUE NOT NULL,
  language_name VARCHAR(100)       NOT NULL
);

-- (Optional) Seed some example languages:
INSERT IGNORE INTO languages (language_code, language_name) VALUES
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


-- 7) USER_LANGUAGES join table
--    Many‐to‐many link between users and languages.
CREATE TABLE IF NOT EXISTS user_languages (
  user_id     INT NOT NULL,
  language_id INT NOT NULL,
  PRIMARY KEY (user_id, language_id),
  FOREIGN KEY (user_id)     REFERENCES users(id)      ON DELETE CASCADE,
  FOREIGN KEY (language_id) REFERENCES languages(id)  ON DELETE CASCADE
);


-- 8) CALENDAR table
--    Consultants’ availability slots; references users(id).
CREATE TABLE IF NOT EXISTS Calendar (
  user_id              INT NOT NULL,
  available_day        ENUM('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday'),
  available_time_start TIME,
  available_time_end   TIME,
  PRIMARY KEY (user_id, available_day, available_time_start),
  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);


-- 9) BOOKINGS table
--    References users(id) for both student_id and consultant_id.
CREATE TABLE IF NOT EXISTS bookings (
  id                INT PRIMARY KEY AUTO_INCREMENT,
  student_id        INT NOT NULL,
  consultant_id     INT NOT NULL,
  status            ENUM('pending','confirmed','cancelled','completed') DEFAULT 'pending',
  booked_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
  scheduled_start   DATETIME,
  scheduled_end     DATETIME,
  reason            ENUM('accommodation','social_life','uni_info','travel_info','company_info'),
  platform          ENUM('zoom','microsoft_teams','google_meet','apple_facetime'),

  FOREIGN KEY (student_id)    REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Automatically mark past confirmed bookings as completed.
UPDATE bookings
SET status = 'completed'
WHERE status = 'confirmed'
  AND scheduled_end < NOW();


-- 10) SESSIONS table
--     One session per booking_id.
CREATE TABLE IF NOT EXISTS sessions (
  id                 INT PRIMARY KEY AUTO_INCREMENT,
  booking_id         INT UNIQUE,   -- each booking only has one session
  video_link         VARCHAR(255),
  started_at         DATETIME,
  ended_at           DATETIME,
  pre_session_notes  TEXT,
  post_session_notes TEXT,
  created_at         DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at         DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE
);


-- 11) MESSAGES table
--     Encrypted messages between users, linked to a booking.
CREATE TABLE IF NOT EXISTS messages (
  id                INT PRIMARY KEY AUTO_INCREMENT,
  sender_id         INT NOT NULL,
  receiver_id       INT NOT NULL,
  booking_id        INT,
  encrypted_message VARBINARY(512) NOT NULL,
  encryption_iv     VARBINARY(16)  NOT NULL,
  is_reported       BOOLEAN DEFAULT FALSE,
  reported_at       DATETIME,
  sent_at           DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at        DATETIME DEFAULT (CURRENT_TIMESTAMP + INTERVAL 3 YEAR),

  FOREIGN KEY (sender_id)   REFERENCES users(id)    ON DELETE CASCADE,
  FOREIGN KEY (receiver_id) REFERENCES users(id)    ON DELETE CASCADE,
  FOREIGN KEY (booking_id)  REFERENCES bookings(id) ON DELETE SET NULL,

  INDEX (booking_id),
  INDEX (sender_id, receiver_id),
  INDEX (sent_at),
  INDEX (expires_at)
);

-- Remove expired messages immediately after creating the table.
DELETE FROM messages
WHERE expires_at < NOW();


-- 12) SUPPORT_TICKETS table
CREATE TABLE IF NOT EXISTS support_tickets (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  user_id     INT NOT NULL,
  subject     VARCHAR(255) NOT NULL,
  description TEXT NOT NULL,
  status      ENUM('open','in_progress','resolved','closed') NOT NULL DEFAULT 'open',
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  resolved_by INT,
  resolved_at DATETIME,

  FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,

  INDEX (user_id),
  INDEX (status)
);


-- 13) UPLOADED_DOCUMENTS table
CREATE TABLE IF NOT EXISTS uploaded_documents (
  id                  INT PRIMARY KEY AUTO_INCREMENT,
  user_id             INT NOT NULL,
  document_name       VARCHAR(255) NOT NULL,
  document_type       ENUM('company','school') NOT NULL,
  upload_date         DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  verification_date   DATETIME,
  is_valid            BOOLEAN DEFAULT FALSE,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,

  INDEX (user_id),
  INDEX (is_valid)
);


-- 14) CONTACT_MESSAGES table (for “Contact Us” form submissions)
CREATE TABLE IF NOT EXISTS contact_messages (
  id           INT PRIMARY KEY AUTO_INCREMENT,
  name         VARCHAR(255) NOT NULL,
  email        VARCHAR(255) NOT NULL,
  message      TEXT NOT NULL,
  submitted_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- 15) REFRESH_TOKENS table
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  token       VARCHAR(64) NOT NULL UNIQUE,
  user_id     INT NOT NULL,
  issued_at   DATETIME NOT NULL,
  expires_at  DATETIME NOT NULL,
  revoked     BOOLEAN NOT NULL DEFAULT FALSE,

  FOREIGN KEY (user_id) REFERENCES users(id)
);

-- 19) Consultant_Reviews table
CREATE TABLE IF NOT EXISTS consultant_reviews (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  booking_id      INT NOT NULL UNIQUE,
  student_id      INT NOT NULL,
  consultant_id   INT NOT NULL,
  rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  review_text     TEXT,
  submitted_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (booking_id) REFERENCES bookings(id) ON DELETE CASCADE,
  FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE CASCADE
);


-- -- 16) Seed Data for Testing Purposes (optional; uses INSERT IGNORE)
-- -- 16.1) Pre‐seeded users (explicit IDs)
-- INSERT IGNORE INTO users (
--   id, first_name, last_name, email, password_hash, role, city, country_name, birthday, gender, access_level, profile_picture
-- ) VALUES
--   (1, 'Alice', 'Student',    'alice@student.com',    'hashed_password_1', 'student',    'New York', 'United States', '2000-01-01', 'female', 'standard', 'alice.jpg'),
--   (2, 'Bob',   'Student',    'bob@student.com',      'hashed_password_2', 'student',    'Berlin',    'Germany',       '1999-02-02', 'male',   'standard', 'bob.jpg'),
--   (3, 'Carol', 'Consultant', 'carol@consult.com',    'hashed_password_3', 'consultant', 'Paris',     'France',        '1995-03-03', 'female', 'standard', 'carol.jpg'),
--   (4, 'Dave',  'Consultant', 'dave@consult.com',     'hashed_password_4', 'consultant', 'Tokyo',     'Japan',         '1993-04-04', 'male',   'standard', 'dave.jpg'),
--   (5, 'Eve',   'Admin',      'eve@admin.com',        'hashed_password_5', 'admin',      'San Francisco','United States','1985-05-05','female','super',  'eve.jpg'),
--   (6, 'Frank', 'Admin',      'frank@admin.com',      'hashed_password_6', 'admin',      'São Paulo', 'Brazil',        '1980-06-06','male',   'super',    'frank.jpg');

-- -- 16.2) Seed Education for Carol (user_id 3)
-- INSERT IGNORE INTO Education (
--   user_id, city_of_study, country_of_study, university_name, course_name,
--   education_start, education_finish, proof_of_education,
--   accommodation, social_life, uni_info, travel_info,
--   zoom, microsoft_teams, google_meet, apple_facetime,
--   is_verified, verified_by, verified_at
-- ) VALUES (
--   3, 'Paris', 'France', 'Sorbonne University', 'International Relations',
--   '2015-09-01','2018-06-30','sorbonne_proof.pdf',
--   TRUE, TRUE, TRUE, TRUE, TRUE, TRUE, FALSE, FALSE, TRUE, 5, NOW()
-- );

-- -- 16.3) Seed Internship for Dave (user_id 4)
-- INSERT IGNORE INTO Internship (
--   user_id, city_of_internship, country_of_internship, company_name, department_name,
--   internship_start, internship_finish, proof_of_internship,
--   accommodation, social_life, company_info, travel_info,
--   zoom, microsoft_teams, google_meet, apple_facetime,
--   is_verified, verified_by, verified_at
-- ) VALUES (
--   4, 'Tokyo', 'Japan','Sony Corporation','Software Engineering',
--   '2016-07-01','2017-12-31','sony_proof.pdf',
--   FALSE, TRUE, TRUE, TRUE, FALSE, TRUE, TRUE, TRUE, TRUE, 6, NOW()
-- );

-- -- 16.4) Seed Calendar availability for Carol (user_id 3) and Dave (user_id 4)
-- INSERT IGNORE INTO Calendar (user_id, available_day, available_time_start, available_time_end) VALUES
--   (3, 'Monday',    '09:00:00','17:00:00'),
--   (4, 'Tuesday',   '10:00:00','18:00:00');

-- -- 16.5) Seed a couple of Bookings
-- INSERT IGNORE INTO bookings (
--   id, student_id, consultant_id, status, booked_at, scheduled_start, scheduled_end, reason, platform
-- ) VALUES
--   (1, 1, 3, 'confirmed', NOW(), '2025-06-05 10:00:00','2025-06-05 11:00:00','uni_info','zoom'),
--   (2, 2, 4, 'confirmed', NOW(), '2025-06-06 11:00:00','2025-06-06 12:00:00','company_info','google_meet');

-- -- 16.6) Seed Sessions
-- INSERT IGNORE INTO sessions (
--   booking_id, video_link, started_at, ended_at, pre_session_notes, post_session_notes
-- ) VALUES
--   (1, 'https://zoom.us/meeting/abc123','2025-06-05 10:00:00','2025-06-05 11:00:00','Started well','Ended successfully'),
--   (2, 'https://meet.google.com/def456','2025-06-06 11:00:00','2025-06-06 12:00:00','Discussed internship','Next steps outlined');

-- -- 16.7) Seed Messages
-- INSERT IGNORE INTO messages (
--   sender_id, receiver_id, booking_id, encrypted_message, encryption_iv, is_reported, reported_at, sent_at, expires_at
-- ) VALUES
--   (1, 3, 1, 0x1234ABCD, 0x0102030405060708, FALSE, NULL, NOW(), DATE_ADD(NOW(), INTERVAL 3 YEAR)),
--   (2, 4, 2, 0xABCD1234, 0x0807060504030201, FALSE, NULL, NOW(), DATE_ADD(NOW(), INTERVAL 3 YEAR));

-- -- 16.8) Seed Support Tickets
-- INSERT IGNORE INTO support_tickets (
--   user_id, subject, description, status, created_at, updated_at, resolved_by, resolved_at
-- ) VALUES
--   (1, 'Account Issue',    'I cannot update my profile.', 'resolved', NOW(), NOW(), 5, NOW()),
--   (2, 'Booking Problem',  'My consultant didn’t show up.', 'in_progress', NOW(), NOW(), NULL, NULL);

-- -- 16.9) Seed Uploaded Documents
-- INSERT IGNORE INTO uploaded_documents (
--   user_id, document_name, document_type, upload_date, verification_date, is_valid
-- ) VALUES
--   (3, 'sorbonne_proof.pdf',   'school', NOW(), NOW(), TRUE),
--   (4, 'sony_proof.pdf',       'company',NOW(), NOW(), TRUE);

-- -- 16.10) Seed Contact Messages (“Contact Us”)
-- INSERT IGNORE INTO contact_messages (
--   name, email, message, submitted_at
-- ) VALUES
--   ('Visitor One', 'visitor1@example.com', 'I have a question about your services.', NOW()),
--   ('Visitor Two', 'visitor2@example.com', 'Can I become a consultant?',      NOW());

-- ─────────────────────────────────────────────────────────────────────────────
-- END OF 01_init.sql
-- ─────────────────────────────────────────────────────────────────────────────