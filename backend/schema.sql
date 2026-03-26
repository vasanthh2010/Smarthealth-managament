-- Smart Hospital Token & Bed Management System
-- MySQL Database Schema
-- Run this file to initialize the database

-- CREATE DATABASE IF NOT EXISTS smart_hospital;
-- USE smart_hospital;

-- ============================================================
-- USERS (Patients)
-- ============================================================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    date_of_birth DATE NOT NULL,
    age INT NOT NULL,
    blood_group VARCHAR(5) NOT NULL,
    address TEXT NOT NULL,
    gender VARCHAR(10) NOT NULL,
    emergency_contact VARCHAR(20),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- ============================================================
-- SUPER ADMIN
-- ============================================================
CREATE TABLE IF NOT EXISTS super_admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    password_hash VARCHAR(256) NOT NULL,
    email VARCHAR(150) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ============================================================
-- HOSPITALS
-- ============================================================
CREATE TABLE IF NOT EXISTS hospitals (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(150),
    location_lat DECIMAL(10, 8),
    location_lng DECIMAL(11, 8),
    established_year INT,
    total_beds INT DEFAULT 0,
    description TEXT,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    login_id VARCHAR(50) UNIQUE,
    password_hash VARCHAR(256),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP NULL
);

-- ============================================================
-- DOCTORS
-- ============================================================
CREATE TABLE IF NOT EXISTS doctors (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    name VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    qualification VARCHAR(150),
    experience_years INT DEFAULT 0,
    consultation_fee DECIMAL(10, 2) DEFAULT 0.00,
    is_available BOOLEAN DEFAULT TRUE,
    avg_consultation_minutes INT DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

-- ============================================================
-- BEDS
-- ============================================================
CREATE TABLE IF NOT EXISTS beds (
    id INT AUTO_INCREMENT PRIMARY KEY,
    hospital_id INT NOT NULL,
    bed_number VARCHAR(20) NOT NULL,
    ward_type ENUM('ICU', 'General', 'Emergency', 'Pediatric', 'Maternity') DEFAULT 'General',
    status ENUM('available', 'occupied') DEFAULT 'available',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

-- ============================================================
-- TOKENS
-- ============================================================
CREATE TABLE IF NOT EXISTS tokens (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    doctor_id INT NOT NULL,
    hospital_id INT NOT NULL,
    token_number INT NOT NULL,
    status ENUM('pending', 'in_service', 'completed', 'cancelled') DEFAULT 'pending',
    booking_date DATE NOT NULL,
    reason TEXT,
    estimated_wait_minutes INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

-- ============================================================
-- AMBULANCE REQUESTS
-- ============================================================
CREATE TABLE IF NOT EXISTS ambulance_requests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    patient_name VARCHAR(100) NOT NULL,
    patient_phone VARCHAR(20) NOT NULL,
    pickup_address TEXT NOT NULL,
    pickup_lat DECIMAL(10, 8),
    pickup_lng DECIMAL(11, 8),
    hospital_id INT,
    status ENUM('requested', 'dispatched', 'completed', 'cancelled') DEFAULT 'requested',
    emergency_type VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL
);

-- ============================================================
-- HOSPITAL REGISTRATION REQUESTS (before approval)
-- ============================================================
CREATE TABLE IF NOT EXISTS hospital_registrations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL,
    address TEXT NOT NULL,
    city VARCHAR(100) NOT NULL,
    state VARCHAR(100) NOT NULL,
    pincode VARCHAR(10) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(150) NOT NULL,
    established_year INT,
    total_beds INT DEFAULT 0,
    description TEXT,
    contact_person VARCHAR(100) NOT NULL,
    contact_designation VARCHAR(100),
    doctors_info JSON,
    status ENUM('pending', 'approved', 'rejected') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP NULL
);

-- ============================================================
-- DEFAULT SUPER ADMIN (password: Admin@123)
-- ============================================================
INSERT INTO super_admins (username, email, password_hash)
VALUES ('superadmin', 'admin@smarthospital.com',
'$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBqEQRs/IOB.G6')
ON DUPLICATE KEY UPDATE username=username;

-- ============================================================
-- SAMPLE APPROVED HOSPITAL (for demo)
-- ============================================================
INSERT INTO hospitals (name, address, city, state, pincode, phone, email,
    location_lat, location_lng, established_year, total_beds, description,
    status, login_id, password_hash)
VALUES (
    'City General Hospital',
    '123 MG Road, Near Central Park',
    'Chennai',
    'Tamil Nadu',
    '600001',
    '044-12345678',
    'info@citygeneralhospital.com',
    13.0827,
    80.2707,
    2005,
    50,
    'A premier multi-specialty hospital serving the community for over 18 years.',
    'approved',
    'HOSP001',
    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBqEQRs/IOB.G6'
) ON DUPLICATE KEY UPDATE name=name;

-- Sample Doctors for demo hospital
INSERT INTO doctors (hospital_id, name, specialization, qualification, experience_years, consultation_fee, avg_consultation_minutes)
VALUES
    (1, 'Dr. Anita Sharma', 'Cardiology', 'MBBS, MD (Cardiology)', 15, 800.00, 15),
    (1, 'Dr. Rajesh Kumar', 'General Medicine', 'MBBS, MD', 10, 400.00, 10),
    (1, 'Dr. Priya Nair', 'Pediatrics', 'MBBS, DCH', 8, 500.00, 10),
    (1, 'Dr. Mohammed Ali', 'Orthopedics', 'MBBS, MS (Ortho)', 12, 700.00, 20),
    (1, 'Dr. Sunita Patel', 'Gynecology', 'MBBS, MS (OBG)', 14, 600.00, 15)
ON DUPLICATE KEY UPDATE name=name;

-- Sample Beds for demo hospital
INSERT INTO beds (hospital_id, bed_number, ward_type, status) VALUES
    (1, 'ICU-01', 'ICU', 'occupied'),
    (1, 'ICU-02', 'ICU', 'available'),
    (1, 'ICU-03', 'ICU', 'occupied'),
    (1, 'GEN-01', 'General', 'available'),
    (1, 'GEN-02', 'General', 'available'),
    (1, 'GEN-03', 'General', 'occupied'),
    (1, 'GEN-04', 'General', 'available'),
    (1, 'GEN-05', 'General', 'occupied'),
    (1, 'EMR-01', 'Emergency', 'available'),
    (1, 'EMR-02', 'Emergency', 'available'),
    (1, 'PED-01', 'Pediatric', 'occupied'),
    (1, 'PED-02', 'Pediatric', 'available'),
    (1, 'MAT-01', 'Maternity', 'available'),
    (1, 'MAT-02', 'Maternity', 'occupied')
ON DUPLICATE KEY UPDATE bed_number=bed_number;
