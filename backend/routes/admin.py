from flask import Blueprint, request, jsonify
import bcrypt
import secrets
import string
import json
from db import query_db
from middleware import require_role

admin_bp = Blueprint('admin', __name__)

def generate_login_id(hospital_name):
    prefix = ''.join(c for c in hospital_name[:4].upper() if c.isalpha()).ljust(4, 'H')
    suffix = ''.join(secrets.choice(string.digits) for _ in range(4))
    return f"HOSP-{prefix}{suffix}"

def generate_password():
    chars = string.ascii_letters + string.digits + '@#$'
    return ''.join(secrets.choice(chars) for _ in range(10))

# ─── DASHBOARD STATS ─────────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/stats', methods=['GET'])
@require_role('super_admin')
def admin_stats(current_user):
    stats = query_db(
        '''SELECT
            (SELECT COUNT(*) FROM hospitals WHERE status='approved') AS total_hospitals,
            (SELECT COUNT(*) FROM hospitals WHERE status='pending') AS pending_hospitals,
            (SELECT COUNT(*) FROM users WHERE is_active=1) AS total_patients,
            (SELECT COUNT(*) FROM doctors) AS total_doctors,
            (SELECT COUNT(*) FROM beds WHERE status='available') AS available_beds,
            (SELECT COUNT(*) FROM beds WHERE status='occupied') AS occupied_beds,
            (SELECT COUNT(*) FROM tokens WHERE booking_date=date('now')) AS today_tokens,
            (SELECT COUNT(*) FROM ambulance_requests WHERE DATE(created_at)=date('now')) AS today_ambulance,
            (SELECT COUNT(*) FROM hospital_registrations WHERE status='pending') AS pending_registrations
        ''',
        one=True
    )
    return jsonify(stats), 200

# ─── ALL HOSPITALS ───────────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/hospitals', methods=['GET'])
@require_role('super_admin')
def all_hospitals(current_user):
    status_filter = request.args.get('status', 'all')
    sql = '''SELECT h.*,
                COUNT(DISTINCT d.id) AS doctor_count,
                COUNT(DISTINCT b.id) AS bed_count
            FROM hospitals h
            LEFT JOIN doctors d ON d.hospital_id = h.id
            LEFT JOIN beds b ON b.hospital_id = h.id'''
    params = []
    if status_filter != 'all':
        sql += ' WHERE h.status=%s'
        params.append(status_filter)
    sql += ' GROUP BY h.id ORDER BY h.created_at DESC'
    hospitals = query_db(sql, params)
    for h in hospitals:
        h.pop('password_hash', None)
        h['created_at'] = str(h['created_at'])
        h['approved_at'] = str(h['approved_at']) if h['approved_at'] else None
        
        if h['status'] == 'approved':
            h['demo_password'] = h.get('demo_password') or 'Admin@123'
        else:
            h['demo_password'] = 'N/A'

    return jsonify(hospitals), 200

# ─── PENDING REGISTRATIONS ────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/registrations', methods=['GET'])
@require_role('super_admin')
def pending_registrations(current_user):
    regs = query_db(
        'SELECT * FROM hospital_registrations ORDER BY created_at DESC'
    )
    result = []
    for r in regs:
        r['created_at'] = str(r['created_at'])
        r['reviewed_at'] = str(r['reviewed_at']) if r['reviewed_at'] else None
        if r['doctors_info'] and isinstance(r['doctors_info'], str):
            try:
                r['doctors_info'] = json.loads(r['doctors_info'])
            except:
                pass
        result.append(r)
    return jsonify(result), 200

# ─── APPROVE HOSPITAL REGISTRATION ───────────────────────────────────────────────
@admin_bp.route('/api/admin/registrations/<int:reg_id>/approve', methods=['POST'])
@require_role('super_admin')
def approve_hospital(reg_id, current_user):
    reg = query_db('SELECT * FROM hospital_registrations WHERE id=%s', (reg_id,), one=True)
    if not reg:
        return jsonify({'error': 'Registration not found'}), 404

    login_id = generate_login_id(reg['name'])
    raw_password = generate_password()
    pw_hash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()

    hospital_id = query_db(
        '''INSERT INTO hospitals (name, address, city, state, pincode, phone, email,
           established_year, total_beds, description, status, login_id, password_hash, demo_password, approved_at)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,'approved',%s,%s,%s,CURRENT_TIMESTAMP)''',
        (reg['name'], reg['address'], reg['city'], reg['state'], reg['pincode'],
         reg['phone'], reg['email'], reg['established_year'], reg['total_beds'],
         reg['description'], login_id, pw_hash, raw_password),
        commit=True
    )

    # Add doctors if provided
    if reg['doctors_info']:
        try:
            doctors = json.loads(reg['doctors_info']) if isinstance(reg['doctors_info'], str) else reg['doctors_info']
            for d in doctors:
                query_db(
                    'INSERT INTO doctors (hospital_id, name, specialization, qualification, experience_years, consultation_fee) VALUES (%s,%s,%s,%s,%s,%s)',
                    (hospital_id, d.get('name',''), d.get('specialization',''),
                     d.get('qualification',''), d.get('experience_years',0), d.get('consultation_fee',0)),
                    commit=True
                )
        except:
            pass

    # Mark registration as approved
    query_db('UPDATE hospital_registrations SET status="approved", reviewed_at=CURRENT_TIMESTAMP WHERE id=%s',
             (reg_id,), commit=True)

    return jsonify({
        'message': 'Hospital approved successfully',
        'hospital_id': hospital_id,
        'login_id': login_id,
        'password': raw_password
    }), 200

# ─── REJECT REGISTRATION ─────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/registrations/<int:reg_id>/reject', methods=['POST'])
@require_role('super_admin')
def reject_hospital_registration(reg_id, current_user):
    query_db('UPDATE hospital_registrations SET status="rejected", reviewed_at=CURRENT_TIMESTAMP WHERE id=%s',
             (reg_id,), commit=True)
    return jsonify({'message': 'Registration rejected'}), 200

# ─── DELETE HOSPITAL ─────────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/hospitals/<int:hospital_id>', methods=['DELETE'])
@require_role('super_admin')
def delete_hospital(hospital_id, current_user):
    hospital = query_db('SELECT id, name FROM hospitals WHERE id=%s', (hospital_id,), one=True)
    if not hospital:
        return jsonify({'error': 'Hospital not found'}), 404
    query_db('DELETE FROM hospitals WHERE id=%s', (hospital_id,), commit=True)
    return jsonify({'message': f'Hospital "{hospital["name"]}" removed'}), 200

# ─── ALL PATIENTS ────────────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/patients', methods=['GET'])
@require_role('super_admin')
def all_patients(current_user):
    search = request.args.get('search', '')
    sql = '''SELECT id, full_name, email, phone, blood_group, gender, age, address,
                date_of_birth, created_at, is_active
            FROM users WHERE 1=1'''
    params = []
    if search:
        sql += ' AND (full_name LIKE %s OR email LIKE %s OR phone LIKE %s)'
        params.extend([f'%{search}%', f'%{search}%', f'%{search}%'])
    sql += ' ORDER BY created_at DESC'
    patients = query_db(sql, params)
    for p in patients:
        p['created_at'] = str(p['created_at'])
        p['date_of_birth'] = str(p['date_of_birth'])
    return jsonify(patients), 200

# ─── DELETE PATIENT ───────────────────────────────────────────────────────────────
@admin_bp.route('/api/admin/patients/<int:patient_id>', methods=['DELETE'])
@require_role('super_admin')
def delete_patient(patient_id, current_user):
    patient = query_db('SELECT id, full_name FROM users WHERE id=%s', (patient_id,), one=True)
    if not patient:
        return jsonify({'error': 'Patient not found'}), 404
    query_db('DELETE FROM users WHERE id=%s', (patient_id,), commit=True)
    return jsonify({'message': f'Patient "{patient["full_name"]}" removed'}), 200

# ─── DIRECT APPROVE EXISTING HOSPITAL ────────────────────────────────────────────
@admin_bp.route('/api/admin/hospitals/<int:hospital_id>/approve', methods=['POST'])
@require_role('super_admin')
def approve_existing_hospital(hospital_id, current_user):
    hospital = query_db('SELECT * FROM hospitals WHERE id=%s', (hospital_id,), one=True)
    if not hospital:
        return jsonify({'error': 'Not found'}), 404

    login_id = generate_login_id(hospital['name'])
    raw_password = generate_password()
    pw_hash = bcrypt.hashpw(raw_password.encode(), bcrypt.gensalt()).decode()
    query_db(
        'UPDATE hospitals SET status="approved", login_id=%s, password_hash=%s, demo_password=%s, approved_at=CURRENT_TIMESTAMP WHERE id=%s',
        (login_id, pw_hash, raw_password, hospital_id), commit=True
    )
    return jsonify({'message': 'Hospital approved', 'login_id': login_id, 'password': raw_password}), 200

# ─────── DOCTOR MANAGEMENT (Admin view) ──────────────────────────────────────────
@admin_bp.route('/api/admin/hospitals/<int:hospital_id>/doctors', methods=['GET'])
@require_role('super_admin')
def hospital_doctors(hospital_id, current_user):
    doctors = query_db('SELECT * FROM doctors WHERE hospital_id=%s', (hospital_id,))
    return jsonify(doctors), 200
