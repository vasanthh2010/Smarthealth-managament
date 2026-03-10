-- Smart Hospital Token & Bed Management System
-- SQLite Database Schema

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    phone TEXT NOT NULL,
    password_hash TEXT NOT NULL,
    date_of_birth DATE NOT NULL,
    age INTEGER NOT NULL,
    blood_group TEXT NOT NULL,
    address TEXT NOT NULL,
    gender TEXT NOT NULL,
    emergency_contact TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

DROP TABLE IF EXISTS super_admins;
CREATE TABLE super_admins (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

DROP TABLE IF EXISTS hospitals;
CREATE TABLE hospitals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    pincode TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT,
    location_lat REAL,
    location_lng REAL,
    established_year INTEGER,
    total_beds INTEGER DEFAULT 0,
    description TEXT,
    status TEXT DEFAULT 'pending', -- 'pending', 'approved', 'rejected'
    login_id TEXT UNIQUE,
    password_hash TEXT,
    demo_password TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    approved_at TIMESTAMP
);

DROP TABLE IF EXISTS doctors;
CREATE TABLE doctors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    specialization TEXT NOT NULL,
    qualification TEXT,
    experience_years INTEGER DEFAULT 0,
    consultation_fee REAL DEFAULT 0.00,
    is_available INTEGER DEFAULT 1,
    avg_consultation_minutes INTEGER DEFAULT 10,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS beds;
CREATE TABLE beds (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hospital_id INTEGER NOT NULL,
    bed_number TEXT NOT NULL,
    ward_type TEXT DEFAULT 'General',
    status TEXT DEFAULT 'available',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS tokens;
CREATE TABLE tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    doctor_id INTEGER NOT NULL,
    hospital_id INTEGER NOT NULL,
    token_number INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    booking_date DATE NOT NULL,
    reason TEXT,
    estimated_wait_minutes INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_at TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id) REFERENCES doctors(id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS ambulance_requests;
CREATE TABLE ambulance_requests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    patient_name TEXT NOT NULL,
    patient_phone TEXT NOT NULL,
    pickup_address TEXT NOT NULL,
    pickup_lat REAL,
    pickup_lng REAL,
    hospital_id INTEGER,
    status TEXT DEFAULT 'requested',
    emergency_type TEXT,
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (hospital_id) REFERENCES hospitals(id) ON DELETE SET NULL
);

DROP TABLE IF EXISTS hospital_registrations;
CREATE TABLE hospital_registrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    state TEXT NOT NULL,
    pincode TEXT NOT NULL,
    phone TEXT NOT NULL,
    email TEXT NOT NULL,
    established_year INTEGER,
    total_beds INTEGER DEFAULT 0,
    description TEXT,
    contact_person TEXT NOT NULL,
    contact_designation TEXT,
    doctors_info TEXT,
    status TEXT DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    reviewed_at TIMESTAMP
);

-- Default Super Admin
INSERT OR IGNORE INTO super_admins (username, email, password_hash)
VALUES ('superadmin', 'admin@smarthospital.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/lewdBqEQRs/IOB.G6');

-- Sample Approved Hospital
INSERT OR IGNORE INTO hospitals (id, name, address, city, state, pincode, phone, email,
    location_lat, location_lng, established_year, total_beds, description,
    status, login_id, password_hash, demo_password)
VALUES (
    1,
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
    '$2b$12$7J0w4qDUNUbKHNoz2tprX.FPFdTtzflMsFW6XAVhMRmSB4sHwCCMq',
    'Admin@123'
);

-- Sample Doctors
INSERT OR IGNORE INTO doctors (id, hospital_id, name, specialization, qualification, experience_years, consultation_fee, avg_consultation_minutes)
VALUES
    (1, 1, 'Dr. Anita Sharma', 'Cardiology', 'MBBS, MD (Cardiology)', 15, 800.00, 15),
    (2, 1, 'Dr. Rajesh Kumar', 'General Medicine', 'MBBS, MD', 10, 400.00, 10),
    (3, 1, 'Dr. Priya Nair', 'Pediatrics', 'MBBS, DCH', 8, 500.00, 10),
    (4, 1, 'Dr. Mohammed Ali', 'Orthopedics', 'MBBS, MS (Ortho)', 12, 700.00, 20),
    (5, 1, 'Dr. Sunita Patel', 'Gynecology', 'MBBS, MS (OBG)', 14, 600.00, 15);

-- Sample Beds
INSERT OR IGNORE INTO beds (id, hospital_id, bed_number, ward_type, status) VALUES
    (1, 1, 'ICU-01', 'ICU', 'occupied'),
    (2, 1, 'ICU-02', 'ICU', 'available'),
    (3, 1, 'ICU-03', 'ICU', 'occupied'),
    (4, 1, 'GEN-01', 'General', 'available'),
    (5, 1, 'GEN-02', 'General', 'available'),
    (6, 1, 'GEN-03', 'General', 'occupied'),
    (7, 1, 'GEN-04', 'General', 'available'),
    (8, 1, 'GEN-05', 'General', 'occupied'),
    (9, 1, 'EMR-01', 'Emergency', 'available'),
    (10, 1, 'EMR-02', 'Emergency', 'available'),
    (11, 1, 'PED-01', 'Pediatric', 'occupied'),
    (12, 1, 'PED-02', 'Pediatric', 'available'),
    (13, 1, 'MAT-01', 'Maternity', 'available'),
    (14, 1, 'MAT-02', 'Maternity', 'occupied');
