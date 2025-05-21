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
