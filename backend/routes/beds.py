from flask import Blueprint, request, jsonify
from db import query_db
from middleware import require_role

beds_bp = Blueprint('beds', __name__)

# ─── GET BEDS FOR A HOSPITAL ──────────────────────────────────────────────────────
@beds_bp.route('/api/beds/<int:hospital_id>', methods=['GET'])
def get_beds(hospital_id):
    ward_type = request.args.get('ward_type')
    sql = 'SELECT * FROM beds WHERE hospital_id=%s'
    params = [hospital_id]
    if ward_type:
        sql += ' AND ward_type=%s'
        params.append(ward_type)
    sql += ' ORDER BY ward_type, bed_number'
    beds = query_db(sql, params)
    for b in beds:
        b['updated_at'] = str(b['updated_at'])
    return jsonify(beds), 200

# ─── GET MY HOSPITAL BEDS (Admin) ────────────────────────────────────────────────
@beds_bp.route('/api/beds/my', methods=['GET'])
@require_role('hospital_admin')
def get_my_beds(current_user):
    beds = query_db(
        'SELECT * FROM beds WHERE hospital_id=%s ORDER BY ward_type, bed_number',
        (current_user['hospital_id'],)
    )
    for b in beds:
        b['updated_at'] = str(b['updated_at'])
    return jsonify(beds), 200

# ─── TOGGLE BED STATUS ────────────────────────────────────────────────────────────
@beds_bp.route('/api/beds/<int:bed_id>/status', methods=['PUT'])
@require_role('hospital_admin')
def update_bed_status(bed_id, current_user):
    data = request.get_json()
    new_status = data.get('status')
    if new_status not in ['available', 'occupied']:
        return jsonify({'error': 'Status must be available or occupied'}), 400

    bed = query_db(
        'SELECT * FROM beds WHERE id=%s AND hospital_id=%s',
        (bed_id, current_user['hospital_id']), one=True
    )
    if not bed:
        return jsonify({'error': 'Bed not found or not your hospital'}), 404

    query_db('UPDATE beds SET status=%s WHERE id=%s', (new_status, bed_id), commit=True)

    # Emit real-time event
    from app import socketio
    socketio.emit('bed_update', {
        'hospital_id': current_user['hospital_id'],
        'bed_id': bed_id,
        'bed_number': bed['bed_number'],
        'ward_type': bed['ward_type'],
        'status': new_status
    }, room=f"hospital_{current_user['hospital_id']}")

    return jsonify({'message': 'Bed status updated', 'bed_id': bed_id, 'status': new_status}), 200

# ─── ADD BED ──────────────────────────────────────────────────────────────────────
@beds_bp.route('/api/beds', methods=['POST'])
@require_role('hospital_admin')
def add_bed(current_user):
    data = request.get_json()
    if not data.get('bed_number') or not data.get('ward_type'):
        return jsonify({'error': 'bed_number and ward_type required'}), 400

    bed_id = query_db(
        'INSERT INTO beds (hospital_id, bed_number, ward_type, status) VALUES (%s,%s,%s,%s)',
        (current_user['hospital_id'], data['bed_number'], data['ward_type'],
         data.get('status', 'available')),
        commit=True
    )
    return jsonify({'message': 'Bed added', 'bed_id': bed_id}), 201

# ─── DELETE BED ──────────────────────────────────────────────────────────────────
@beds_bp.route('/api/beds/<int:bed_id>', methods=['DELETE'])
@require_role('hospital_admin')
def delete_bed(bed_id, current_user):
    bed = query_db(
        'SELECT id FROM beds WHERE id=%s AND hospital_id=%s',
        (bed_id, current_user['hospital_id']), one=True
    )
    if not bed:
        return jsonify({'error': 'Bed not found'}), 404
    query_db('DELETE FROM beds WHERE id=%s', (bed_id,), commit=True)
    return jsonify({'message': 'Bed removed'}), 200
