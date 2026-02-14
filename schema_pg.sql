-- StrengerChat Pro - Postgres Database Schema (Final Stable Version)
-- Optimized for PostgreSQL 14+

-- 1. Users Table
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    gender VARCHAR(10) NOT NULL,
    avatar_type VARCHAR(10) DEFAULT 'default',
    age INT,
    bio TEXT,
    is_premium BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. Sessions & Geo-Location Table (PostGIS is overkill, simple float for now)
CREATE TABLE IF NOT EXISTS active_sessions (
    user_id INT PRIMARY KEY,
    socket_id VARCHAR(100),
    latitude FLOAT,
    longitude FLOAT,
    status VARCHAR(20) DEFAULT 'idle',
    looking_for VARCHAR(10) DEFAULT 'both',
    last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_user_session FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- 3. Reports Table
CREATE TABLE IF NOT EXISTS reports (
    id SERIAL PRIMARY KEY,
    reporter_id INT,
    reported_id INT,
    reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_reporter FOREIGN KEY (reporter_id) REFERENCES users(id) ON DELETE SET NULL,
    CONSTRAINT fk_reported FOREIGN KEY (reported_id) REFERENCES users(id) ON DELETE CASCADE
);
