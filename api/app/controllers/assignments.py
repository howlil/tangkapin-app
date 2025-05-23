from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.models import Assignment, Report, User, db
from datetime import datetime

assignments_bp = Blueprint('assignments', __name__)

@assignments_bp.route('/', methods=['GET'])
@jwt_required()
def get_assignments():
    """Get assignments berdasarkan role user"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        if user_role == 'officer':
            # Officer lihat assignment miliknya
            assignments = Assignment.query.filter_by(officer_id=user_id).order_by(Assignment.created_at.desc()).all()
        elif user_role == 'admin':
            # Admin lihat semua assignment
            assignments = Assignment.query.order_by(Assignment.created_at.desc()).all()
        else:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'assignments': [assignment.to_dict() for assignment in assignments],
            'total': len(assignments)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/create', methods=['POST'])
@jwt_required()
def create_assignment():
    """Create assignment baru (Admin only)"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get('role') != 'admin':
            return jsonify({'error': 'Hanya admin yang bisa create assignment'}), 403
        
        data = request.get_json()
        
        # Validasi input
        required_fields = ['report_id', 'officer_id']
        for field in required_fields:
            if not data.get(field):
                return jsonify({'error': f'{field} diperlukan'}), 400
        
        # Validasi report exists
        report = Report.query.get(data['report_id'])
        if not report:
            return jsonify({'error': 'Report tidak ditemukan'}), 404
        
        # Validasi officer exists dan role = officer
        officer = User.query.filter_by(id=data['officer_id'], role='officer', is_active=True).first()
        if not officer:
            return jsonify({'error': 'Officer tidak ditemukan'}), 404
        
        # Cek apakah sudah ada assignment untuk report ini
        existing = Assignment.query.filter_by(report_id=data['report_id']).first()
        if existing:
            return jsonify({'error': 'Report sudah memiliki assignment'}), 400
        
        # Buat assignment baru
        assignment = Assignment(
            report_id=data['report_id'],
            officer_id=data['officer_id'],
            assigned_by=user_id,
            notes=data.get('notes')
        )
        
        # Update status report ke ASSIGNED
        report.status = 'ASSIGNED'
        
        db.session.add(assignment)
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment berhasil dibuat',
            'assignment': assignment.to_dict()
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/<assignment_id>', methods=['GET'])
@jwt_required()
def get_assignment_detail(assignment_id):
    """Get detail assignment"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'error': 'Assignment tidak ditemukan'}), 404
        
        # Officer hanya bisa lihat assignmentnya sendiri
        if user_role == 'officer' and assignment.officer_id != user_id:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'assignment': assignment.to_dict()
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/<assignment_id>/accept', methods=['PUT'])
@jwt_required()
def accept_assignment(assignment_id):
    """Officer accept assignment"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get('role') != 'officer':
            return jsonify({'error': 'Hanya officer yang bisa accept assignment'}), 403
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'error': 'Assignment tidak ditemukan'}), 404
        
        if assignment.officer_id != user_id:
            return jsonify({'error': 'Bukan assignment Anda'}), 403
        
        if assignment.status != 'PENDING':
            return jsonify({'error': 'Assignment sudah tidak pending'}), 400
        
        # Update status assignment
        assignment.status = 'ACCEPTED'
        assignment.updated_at = datetime.utcnow()
        
        # Update status report
        report = Report.query.get(assignment.report_id)
        report.status = 'IN_PROGRESS'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment berhasil diterima',
            'assignment': assignment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/<assignment_id>/reject', methods=['PUT'])
@jwt_required()
def reject_assignment(assignment_id):
    """Officer reject assignment"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get('role') != 'officer':
            return jsonify({'error': 'Hanya officer yang bisa reject assignment'}), 403
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'error': 'Assignment tidak ditemukan'}), 404
        
        if assignment.officer_id != user_id:
            return jsonify({'error': 'Bukan assignment Anda'}), 403
        
        if assignment.status != 'PENDING':
            return jsonify({'error': 'Assignment sudah tidak pending'}), 400
        
        data = request.get_json()
        reject_reason = data.get('notes', 'No reason provided')
        
        # Update status assignment
        assignment.status = 'REJECTED'
        assignment.notes = reject_reason
        assignment.updated_at = datetime.utcnow()
        
        # Update status report kembali ke VERIFIED
        report = Report.query.get(assignment.report_id)
        report.status = 'VERIFIED'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment berhasil ditolak',
            'assignment': assignment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/<assignment_id>/complete', methods=['PUT'])
@jwt_required()
def complete_assignment(assignment_id):
    """Officer complete assignment"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        
        if claims.get('role') != 'officer':
            return jsonify({'error': 'Hanya officer yang bisa complete assignment'}), 403
        
        assignment = Assignment.query.get(assignment_id)
        if not assignment:
            return jsonify({'error': 'Assignment tidak ditemukan'}), 404
        
        if assignment.officer_id != user_id:
            return jsonify({'error': 'Bukan assignment Anda'}), 403
        
        if assignment.status not in ['ACCEPTED', 'IN_PROGRESS']:
            return jsonify({'error': 'Assignment belum di-accept'}), 400
        
        data = request.get_json()
        completion_notes = data.get('notes', '')
        
        # Calculate response time if available
        response_time = None
        if assignment.created_at:
            time_diff = datetime.utcnow() - assignment.created_at
            response_time = int(time_diff.total_seconds())
        
        # Update status assignment
        assignment.status = 'COMPLETED'
        assignment.notes = completion_notes
        assignment.response_time = response_time
        assignment.updated_at = datetime.utcnow()
        
        # Update status report
        report = Report.query.get(assignment.report_id)
        report.status = 'COMPLETED'
        
        db.session.commit()
        
        return jsonify({
            'message': 'Assignment berhasil diselesaikan',
            'assignment': assignment.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@assignments_bp.route('/status/<status>', methods=['GET'])
@jwt_required()
def get_assignments_by_status(status):
    """Filter assignments berdasarkan status"""
    try:
        user_id = get_jwt_identity()
        claims = get_jwt()
        user_role = claims.get('role')
        
        valid_statuses = ['PENDING', 'ACCEPTED', 'IN_PROGRESS', 'COMPLETED', 'REJECTED']
        if status not in valid_statuses:
            return jsonify({'error': 'Status tidak valid'}), 400
        
        if user_role == 'officer':
            assignments = Assignment.query.filter_by(
                officer_id=user_id, 
                status=status
            ).order_by(Assignment.created_at.desc()).all()
        elif user_role == 'admin':
            assignments = Assignment.query.filter_by(
                status=status
            ).order_by(Assignment.created_at.desc()).all()
        else:
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'assignments': [assignment.to_dict() for assignment in assignments],
            'total': len(assignments),
            'status': status
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500