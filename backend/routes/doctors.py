from flask import Blueprint, request, jsonify
from db import query_db
from middleware import require_role

doctors_bp = Blueprint('doctors', __name__)

@doctors_bp.route('/api/doctors/<int:hospital_id>', methods=['GET'])
def get_doctors(hospital_id):
    doctors = query_db(
        '''SELECT d.*,
            COUNT(CASE WHEN t.status='pending' AND t.booking_date=date('now') THEN 1 END) AS queue_count,
            MAX(CASE WHEN t.status='in_service' THEN t.token_number END) AS current_token
            FROM doctors d
            LEFT JOIN tokens t ON t.doctor_id = d.id
            WHERE d.hospital_id=%s
            GROUP BY d.id ORDER BY d.specialization''',
        (hospital_id,)
    )
    return jsonify(doctors), 200

@doctors_bp.route('/api/doctors/my', methods=['GET'])
@require_role('hospital_admin')
def my_doctors(current_user):
    doctors = query_db(
        '''SELECT d.*,
            COUNT(CASE WHEN t.status='pending' AND t.booking_date=date('now') THEN 1 END) AS queue_count
            FROM doctors d
            LEFT JOIN tokens t ON t.doctor_id=d.id
            WHERE d.hospital_id=%s GROUP BY d.id ORDER BY d.specialization''',
        (current_user['hospital_id'],)
    )
    return jsonify(doctors), 200

@doctors_bp.route('/api/doctors', methods=['POST'])
@require_role('hospital_admin')
def add_doctor(current_user):
    data = request.get_json()
    if not data.get('name') or not data.get('specialization'):
        return jsonify({'error': 'name and specialization required'}), 400
    doc_id = query_db(
        '''INSERT INTO doctors (hospital_id, name, specialization, qualification,
           experience_years, consultation_fee, avg_consultation_minutes)
           VALUES (%s,%s,%s,%s,%s,%s,%s)''',
        (current_user['hospital_id'], data['name'], data['specialization'],
         data.get('qualification',''), data.get('experience_years', 0),
         data.get('consultation_fee', 0), data.get('avg_consultation_minutes', 10)),
        commit=True
    )
    return jsonify({'message': 'Doctor added', 'doctor_id': doc_id}), 201

@doctors_bp.route('/api/doctors/<int:doc_id>/availability', methods=['PUT'])
@require_role('hospital_admin')
def toggle_doctor_availability(doc_id, current_user):
    data = request.get_json()
    doc = query_db(
        'SELECT id FROM doctors WHERE id=%s AND hospital_id=%s',
        (doc_id, current_user['hospital_id']), one=True
    )
    if not doc:
        return jsonify({'error': 'Not found'}), 404
    query_db('UPDATE doctors SET is_available=%s WHERE id=%s',
             (data.get('is_available', True), doc_id), commit=True)
    return jsonify({'message': 'Availability updated'}), 200

@doctors_bp.route('/api/doctors/<int:doc_id>', methods=['DELETE'])
@require_role('hospital_admin')
def delete_doctor(doc_id, current_user):
    doc = query_db('SELECT id FROM doctors WHERE id=%s AND hospital_id=%s',
                   (doc_id, current_user['hospital_id']), one=True)
    if not doc:
        return jsonify({'error': 'Not found'}), 404
    query_db('DELETE FROM doctors WHERE id=%s', (doc_id,), commit=True)
    return jsonify({'message': 'Doctor removed'}), 200
