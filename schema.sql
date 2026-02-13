-- StrengerChat Pro - MySQL Database Schema (Final Stable Version)
-- Optimized for ALL MySQL/MariaDB versions

SET FOREIGN_KEY_CHECKS = 0;

CREATE DATABASE IF NOT EXISTS strengerchat_pro;
USE strengerchat_pro;

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    gender ENUM('male', 'female', 'other') NOT NULL,
    avatar_type ENUM('boy', 'girl', 'default') DEFAULT 'default',
    age INT,
    bio TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 2. Sessions & Geo-Location Table
CREATE TABLE IF NOT EXISTS active_sessions (
    user_id INT PRIMARY KEY,
    socket_id VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    location_point POINT NOT NULL,
    status ENUM('searching', 'chatting', 'idle') DEFAULT 'idle',
    looking_for ENUM('male', 'female', 'both') DEFAULT 'both',
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    SPATIAL INDEX(location_point),
    CONSTRAINT fk_user_session FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- 3. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id INT AUTO_INCREMENT PRIMARY KEY,
    reporter_id INT,
    reported_id INT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reporter FOREIGN KEY (reporter_id) REFERENCES users(id),
    CONSTRAINT fk_reported FOREIGN KEY (reported_id) REFERENCES users(id)
) ENGINE=InnoDB;

SET FOREIGN_KEY_CHECKS = 1;
