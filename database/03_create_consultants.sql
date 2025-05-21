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
