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
