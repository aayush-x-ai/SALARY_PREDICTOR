CREATE DATABASE IF NOT EXISTS salary_predictor
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE salary_predictor;

CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS predictions (
    prediction_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    education VARCHAR(100) NOT NULL,
    skills VARCHAR(500) NOT NULL,
    experience INT NULL,
    experience_months INT NOT NULL DEFAULT 0,
    city VARCHAR(100) NOT NULL,
    domain VARCHAR(100) NOT NULL,
    job_role VARCHAR(100) NOT NULL,
    predicted_salary DECIMAL(12, 2) NOT NULL,
    prediction_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_predictions_user_date (user_id, prediction_date),
    CONSTRAINT fk_prediction_user
        FOREIGN KEY (user_id) REFERENCES users(user_id)
        ON DELETE CASCADE
);
