CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    surname VARCHAR(100),
    role VARCHAR(20),
    email VARCHAR(255) UNIQUE,
    password TEXT,
    reset_token VARCHAR(255),
    token_expiry DATETIME
);