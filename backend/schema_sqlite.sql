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
    user_id INTEGER, -- Nullable for offline booking
    doctor_id INTEGER NOT NULL,
    hospital_id INTEGER NOT NULL,
    token_number INTEGER NOT NULL,
    status TEXT DEFAULT 'pending',
    booking_date DATE NOT NULL,
    reason TEXT,
    estimated_wait_minutes INTEGER DEFAULT 0,
    is_offline INTEGER DEFAULT 0,
    offline_name TEXT,
    offline_phone TEXT,
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
    (5, 1, 'Dr. Sunita Patel', 'Gynecology', 'MBBS, MS (OBG)', 14, 600.00, 15),
    (6, 1, 'Dr. Vijay K', 'Neurology', 'MBBS, DM', 12, 1000.00, 20),
    (7, 1, 'Dr. Lakshmi R', 'Dermatology', 'MBBS, MD', 7, 500.00, 15),
    (8, 1, 'Dr. Arun Singh', 'ENT', 'MBBS, MS', 9, 450.00, 10),
    (9, 1, 'Dr. Meera J', 'Psychiatry', 'MBBS, MD', 11, 750.00, 15),
    (10, 1, 'Dr. Sanjay G', 'Urology', 'MBBS, MCh', 13, 900.00, 20);

-- Sample Beds (Increased count)
INSERT OR IGNORE INTO beds (hospital_id, bed_number, ward_type, status) VALUES
    (1, 'ICU-01', 'ICU', 'occupied'), (1, 'ICU-02', 'ICU', 'available'), (1, 'ICU-03', 'ICU', 'occupied'), (1, 'ICU-04', 'ICU', 'available'), (1, 'ICU-05', 'ICU', 'available'),
    (1, 'GEN-01', 'General', 'available'), (1, 'GEN-02', 'General', 'available'), (1, 'GEN-03', 'General', 'occupied'), (1, 'GEN-04', 'General', 'available'), (1, 'GEN-05', 'General', 'occupied'),
    (1, 'GEN-06', 'General', 'available'), (1, 'GEN-07', 'General', 'available'), (1, 'GEN-08', 'General', 'available'), (1, 'GEN-09', 'General', 'occupied'), (1, 'GEN-10', 'General', 'available'),
    (1, 'GEN-11', 'General', 'available'), (1, 'GEN-12', 'General', 'available'), (1, 'GEN-13', 'General', 'available'), (1, 'GEN-14', 'General', 'available'), (1, 'GEN-15', 'General', 'available'),
    (1, 'EMR-01', 'Emergency', 'available'), (1, 'EMR-02', 'Emergency', 'available'), (1, 'EMR-03', 'Emergency', 'occupied'), (1, 'EMR-04', 'Emergency', 'available'), (1, 'EMR-05', 'Emergency', 'available'),
    (1, 'PED-01', 'Pediatric', 'occupied'), (1, 'PED-02', 'Pediatric', 'available'), (1, 'PED-03', 'Pediatric', 'available'), (1, 'PED-04', 'Pediatric', 'available'), (1, 'PED-05', 'Pediatric', 'available'),
    (1, 'MAT-01', 'Maternity', 'available'), (1, 'MAT-02', 'Maternity', 'occupied'), (1, 'MAT-03', 'Maternity', 'available'), (1, 'MAT-04', 'Maternity', 'available'), (1, 'MAT-05', 'Maternity', 'available');

-- ─── PERFORMANCE INDEXES ──────────────────────────────────────────────────────
-- These speed up the dashboard stats query and common filters significantly
CREATE INDEX IF NOT EXISTS idx_hospitals_status ON hospitals(status);
CREATE INDEX IF NOT EXISTS idx_users_is_active ON users(is_active);
CREATE INDEX IF NOT EXISTS idx_beds_status ON beds(status);
CREATE INDEX IF NOT EXISTS idx_beds_hospital ON beds(hospital_id);
CREATE INDEX IF NOT EXISTS idx_tokens_booking_date ON tokens(booking_date);
CREATE INDEX IF NOT EXISTS idx_tokens_hospital ON tokens(hospital_id);
CREATE INDEX IF NOT EXISTS idx_tokens_status ON tokens(status);
CREATE INDEX IF NOT EXISTS idx_ambulance_created ON ambulance_requests(created_at);
CREATE INDEX IF NOT EXISTS idx_registrations_status ON hospital_registrations(status);
CREATE INDEX IF NOT EXISTS idx_doctors_hospital ON doctors(hospital_id);

