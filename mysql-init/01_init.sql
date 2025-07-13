-- ─────────────────────────────────────────────────────────────────────────────
-- 01_init.sql
-- Creates every table (and seeds lookup data) in the correct order. No syntax errors.
-- ─────────────────────────────────────────────────────────────────────────────

-- 1) Create (or switch to) the “easyabroad” schema
-- CREATE SCHEMA IF NOT EXISTS easyabroad;
USE easyabroad;

-- 2) COUNTRIES table
--    Must come before any table that references countries(country_name).
CREATE TABLE IF NOT EXISTS countries (
  id            INT AUTO_INCREMENT PRIMARY KEY,
  country_name  VARCHAR(100) NOT NULL UNIQUE,
  country_code  CHAR(2)     NOT NULL UNIQUE
);

-- Inserts full list of countries into countries table.
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
  id                          INT AUTO_INCREMENT PRIMARY KEY,
  first_name                  VARCHAR(255)           NOT NULL,
  last_name                   VARCHAR(255)           NOT NULL,
  email                       VARCHAR(255) UNIQUE    NOT NULL,
  password_hash               VARCHAR(255)           NOT NULL,
  role                        ENUM('student','consultant','admin') NOT NULL,
  city                        VARCHAR(255),
  country_name                VARCHAR(100)           NULL,
  birthday                    DATE,
  gender                      ENUM('male','female','other'),
  access_level                ENUM('standard','super') DEFAULT 'standard',
  profile_picture             VARCHAR(255),

  reset_token                 VARCHAR(255),
  token_expiry                DATETIME,

  is_verified                 BOOLEAN DEFAULT FALSE,
  verification_token          VARCHAR(255),
  verification_token_expiry   DATETIME,

  is_active                   ENUM('active', 'inactive', 'deleted') DEFAULT 'active',
  created_at                  DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at                  DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_users_countries
    FOREIGN KEY (country_name) REFERENCES countries(country_name)
      ON UPDATE CASCADE
      ON DELETE RESTRICT
);


-- 4) EDUCATION table
--    References users(id) and countries(country_name).
CREATE TABLE IF NOT EXISTS Education (
  user_id           INT PRIMARY KEY,
  public_id   VARCHAR(36) UNIQUE DEFAULT NULL,
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
  latitude REAL,
  longitude REAL,
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
  public_id   VARCHAR(36) UNIQUE DEFAULT NULL,
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
  latitude REAL,
  longitude REAL,
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

-- Insert Languages into the languages table.
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


-- 8) CONSULTANT_AVAILABILITY table
--    Consultants’ availability slots; references users(id).
CREATE TABLE IF NOT EXISTS consultant_availability (
  id             INT AUTO_INCREMENT PRIMARY KEY,
  consultant_id  INT NOT NULL,
  days_of_week   JSON     NOT NULL,    -- e.g. [1,3,5]
  start_time     VARCHAR(5) NOT NULL,  -- "09:30"
  end_time       VARCHAR(5) NOT NULL,  -- "10:30"
  timezone       VARCHAR(50) DEFAULT NULL, -- e.g. "Europe/Berlin"  
  FOREIGN KEY (consultant_id) REFERENCES users(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- 9) Appointments table
CREATE TABLE IF NOT EXISTS appointments (
  id INT AUTO_INCREMENT PRIMARY KEY,
  public_id   VARCHAR(36) UNIQUE DEFAULT NULL,
  consultant_id INT NOT NULL,
  consultant_public_id VARCHAR(36) DEFAULT NULL,
  student_id INT NOT NULL,
  date DATE NOT NULL,
  start_time VARCHAR(5) NOT NULL,
  end_time VARCHAR(5) NOT NULL,
  reason VARCHAR(255),
  platform VARCHAR(50),
  status ENUM('pending','upcoming','previous','rejected') DEFAULT 'pending',
  meeting_link VARCHAR(255),
  rejection_reason VARCHAR(255),
  cancellation_reason VARCHAR(255),
  type VARCHAR(32) NOT NULL,
  timezone VARCHAR(50) DEFAULT NULL,
  FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
  info VARCHAR(255) NULL
);

-- 10a) CONVERSATIONS table
CREATE TABLE conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    public_id VARCHAR(36) UNIQUE,
    user_a_id INT NOT NULL,
    user_b_id INT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_a_id) REFERENCES users(id),
    FOREIGN KEY (user_b_id) REFERENCES users(id)
);

-- 10b) MESSAGES table
CREATE TABLE IF NOT EXISTS messages (
  id                  INT PRIMARY KEY AUTO_INCREMENT,
  public_id           VARCHAR(36) UNIQUE DEFAULT NULL,
  sender_id           INT NOT NULL,
  receiver_id         INT NOT NULL,
  conversation_id     INT DEFAULT NULL,
  booking_id          INT,
  encrypted_message   BLOB NOT NULL,
  encryption_iv       VARBINARY(16) NOT NULL,
  is_reported         BOOLEAN DEFAULT FALSE,
  reported_at         DATETIME,
  sent_at             DATETIME DEFAULT CURRENT_TIMESTAMP,
  expires_at          DATETIME DEFAULT (CURRENT_TIMESTAMP + INTERVAL 3 YEAR),
  hidden_for_user_ids TEXT DEFAULT NULL,

  FOREIGN KEY (booking_id)      REFERENCES appointments(id) ON DELETE CASCADE,
  FOREIGN KEY (sender_id)       REFERENCES users(id)        ON DELETE CASCADE,
  FOREIGN KEY (receiver_id)     REFERENCES users(id)        ON DELETE CASCADE,
  FOREIGN KEY (conversation_id) REFERENCES conversations(id) ON DELETE CASCADE,

  INDEX (booking_id),
  INDEX (sender_id, receiver_id),
  INDEX (sent_at),
  INDEX (expires_at),
  INDEX (conversation_id)
);

-- Remove expired messages immediately after creating the table.
DELETE FROM messages
WHERE expires_at < NOW();


-- 11a) SUPPORT_TICKETS table
CREATE TABLE IF NOT EXISTS support_tickets (
  id          INT PRIMARY KEY AUTO_INCREMENT,
  public_id   VARCHAR(36) UNIQUE DEFAULT NULL,
  user_id     INT NOT NULL,
  subject     VARCHAR(100) NOT NULL,
  description VARCHAR(500) NOT NULL,
  status      ENUM('open','in_progress','resolved','closed') NOT NULL DEFAULT 'open',
  created_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at  DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  resolved_by INT,
  resolved_at DATETIME,

  FOREIGN KEY (user_id)     REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (resolved_by) REFERENCES users(id) ON DELETE SET NULL,

  INDEX (user_id),
  INDEX (status),
  INDEX (public_id)
);

-- 11b) SUPPORT_TICKET_MESSAGES table
CREATE TABLE IF NOT EXISTS support_ticket_messages (
  id INT PRIMARY KEY AUTO_INCREMENT,
  ticket_id INT NOT NULL,
  sender_id INT NOT NULL,
  message VARCHAR(500) NOT NULL,
  sent_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (ticket_id) REFERENCES support_tickets(id) ON DELETE CASCADE,
  FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,

  INDEX (ticket_id),
  INDEX (sender_id)
);


-- 12) REFRESH_TOKENS table
CREATE TABLE IF NOT EXISTS refresh_tokens (
  id          INT AUTO_INCREMENT PRIMARY KEY,
  token       VARCHAR(64) NOT NULL UNIQUE,
  user_id     INT NOT NULL,
  issued_at   DATETIME NOT NULL,
  expires_at  DATETIME NOT NULL,
  revoked     BOOLEAN NOT NULL DEFAULT FALSE,

  FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);



-- 13) Consultant_Reviews table
CREATE TABLE IF NOT EXISTS consultant_reviews (
  id              INT PRIMARY KEY AUTO_INCREMENT,
  public_id   VARCHAR(36) UNIQUE DEFAULT NULL,
  booking_id      INT NOT NULL UNIQUE,
  student_id      INT NOT NULL,
  consultant_id   INT NOT NULL,
  rating          TINYINT NOT NULL CHECK (rating BETWEEN 1 AND 5),
  review_text     TEXT,
  submitted_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

  FOREIGN KEY (booking_id) REFERENCES appointments(id) ON DELETE CASCADE,
  FOREIGN KEY (student_id) REFERENCES users(id) ON DELETE CASCADE,
  FOREIGN KEY (consultant_id) REFERENCES users(id) ON DELETE CASCADE
);


-- 14) notifications table
CREATE TABLE notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    type VARCHAR(50) DEFAULT 'info',
    is_read BOOLEAN DEFAULT FALSE,
    redirect_url VARCHAR(255) DEFAULT '#',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);
-- ─────────────────────────────────────────────────────────────────────────────
-- END OF 01_init.sql
-- ─────────────────────────────────────────────────────────────────────────────