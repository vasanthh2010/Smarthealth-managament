from flask import Blueprint, request, jsonify
import bcrypt
import jwt
import datetime
from db import query_db
from config import Config

auth_bp = Blueprint('auth', __name__)

def generate_token(payload):
    payload['exp'] = datetime.datetime.utcnow() + datetime.timedelta(hours=Config.JWT_EXPIRY_HOURS)
    return jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')

# ─── PATIENT SIGNUP ─────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/patient/signup', methods=['POST'])
def patient_signup():
    data = request.get_json()
    required = ['full_name', 'email', 'phone', 'password', 'date_of_birth', 'age',
                'blood_group', 'address', 'gender']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    existing = query_db('SELECT id FROM users WHERE email=%s', (data['email'],), one=True)
    if existing:
        return jsonify({'error': 'Email already registered'}), 409

    pw_hash = bcrypt.hashpw(data['password'].encode(), bcrypt.gensalt()).decode()
    user_id = query_db(
        '''INSERT INTO users (full_name, email, phone, password_hash, date_of_birth,
           age, blood_group, address, gender, emergency_contact)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        (data['full_name'], data['email'], data['phone'], pw_hash,
         data['date_of_birth'], data['age'], data['blood_group'],
         data['address'], data['gender'], data.get('emergency_contact', '')),
        commit=True
    )
    token = generate_token({'user_id': user_id, 'role': 'patient', 'name': data['full_name']})
    return jsonify({'message': 'Signup successful', 'token': token, 'user_id': user_id,
                    'name': data['full_name'], 'role': 'patient'}), 201

# ─── PATIENT LOGIN ───────────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/patient/login', methods=['POST'])
def patient_login():
    data = request.get_json()
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    user = query_db('SELECT * FROM users WHERE email=%s AND is_active=1', (data['email'],), one=True)
    if not user:
        return jsonify({'error': 'Invalid email or password'}), 401
    if not bcrypt.checkpw(data['password'].encode(), user['password_hash'].encode()):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = generate_token({'user_id': user['id'], 'role': 'patient', 'name': user['full_name']})
    return jsonify({'message': 'Login successful', 'token': token, 'user_id': user['id'],
                    'name': user['full_name'], 'role': 'patient'}), 200

# ─── HOSPITAL ADMIN LOGIN ────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/hospital/login', methods=['POST'])
def hospital_login():
    data = request.get_json()
    if not data.get('login_id') or not data.get('password'):
        return jsonify({'error': 'Login ID and password required'}), 400

    hospital = query_db(
        'SELECT * FROM hospitals WHERE login_id=%s AND status="approved"',
        (data['login_id'],), one=True
    )
    if not hospital:
        return jsonify({'error': 'Invalid login ID or hospital not approved'}), 401
    if not bcrypt.checkpw(data['password'].encode(), hospital['password_hash'].encode()):
        return jsonify({'error': 'Invalid password'}), 401

    token = generate_token({'hospital_id': hospital['id'], 'role': 'hospital_admin',
                            'name': hospital['name']})
    return jsonify({'message': 'Login successful', 'token': token,
                    'hospital_id': hospital['id'], 'name': hospital['name'],
                    'role': 'hospital_admin'}), 200

# ─── SUPER ADMIN LOGIN ───────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/admin/login', methods=['POST'])
def admin_login():
    data = request.get_json()
    if not data.get('username') or not data.get('password'):
        return jsonify({'error': 'Username and password required'}), 400

    admin = query_db('SELECT * FROM super_admins WHERE username=%s', (data['username'],), one=True)
    if not admin:
        return jsonify({'error': 'Invalid credentials'}), 401
    if not bcrypt.checkpw(data['password'].encode(), admin['password_hash'].encode()):
        return jsonify({'error': 'Invalid credentials'}), 401

    token = generate_token({'admin_id': admin['id'], 'role': 'super_admin',
                            'name': admin['username']})
    return jsonify({'message': 'Login successful', 'token': token,
                    'admin_id': admin['id'], 'name': admin['username'],
                    'role': 'super_admin'}), 200

# ─── HOSPITAL REGISTRATION REQUEST ──────────────────────────────────────────────
@auth_bp.route('/api/auth/hospital/register', methods=['POST'])
def hospital_register():
    data = request.get_json()
    required = ['name', 'address', 'city', 'state', 'pincode', 'phone', 'email',
                'contact_person', 'total_beds']
    for field in required:
        if not data.get(field):
            return jsonify({'error': f'{field} is required'}), 400

    import json
    reg_id = query_db(
        '''INSERT INTO hospital_registrations (name, address, city, state, pincode, phone,
           email, established_year, total_beds, description, contact_person,
           contact_designation, doctors_info)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
        (data['name'], data['address'], data['city'], data['state'], data['pincode'],
         data['phone'], data['email'], data.get('established_year'),
         data['total_beds'], data.get('description', ''),
         data['contact_person'], data.get('contact_designation', ''),
         json.dumps(data.get('doctors_info', []))),
        commit=True
    )
    return jsonify({'message': 'Registration submitted successfully. Await admin approval.',
                    'registration_id': reg_id}), 201

# ─── GET CURRENT PATIENT ────────────────────────────────────────────────────────
@auth_bp.route('/api/auth/me', methods=['GET'])
def get_me():
    from middleware import get_current_user
    user_payload, err = get_current_user()
    if err:
        return jsonify({'error': err}), 401
    if user_payload.get('role') != 'patient':
        return jsonify({'error': 'Not a patient'}), 403
    user = query_db(
        'SELECT id, full_name, email, phone, blood_group, age, gender, address, date_of_birth FROM users WHERE id=%s',
        (user_payload['user_id'],), one=True
    )
    if not user:
        return jsonify({'error': 'Not found'}), 404
    user['date_of_birth'] = str(user['date_of_birth'])
    return jsonify(user), 200
