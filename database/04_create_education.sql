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
  verified_by INT,
  verified_at DATETIME,
  status VARCHAR(20) NOT NULL DEFAULT 'pending'
    CHECK (status IN ('pending', 'accepted', 'rejected')),
  short_note TEXT,

  FOREIGN KEY (user_id) REFERENCES users(id),
  FOREIGN KEY (verified_by) REFERENCES users(id),
  FOREIGN KEY (country_of_study) REFERENCES countries(country_name)
);
