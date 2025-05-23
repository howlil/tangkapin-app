from app.models import Assignment, User, db
from app.utils.logger import logger
from datetime import datetime

class AssignmentController:
    @staticmethod
    def get_all_assignments(user_id=None, status=None):
        """Get all assignments, optionally filtered by officer_id or status"""
        try:
            query = Assignment.query
            
            if user_id:
                # Filter assignments where user is officer or admin
                query = query.filter_by(officer_id=user_id)
                
            if status:
                query = query.filter_by(status=status)
                
            # Sort by most recent first
            query = query.order_by(Assignment.created_at.desc())
            
            assignments = query.all()
            return {'assignments': [a.to_dict() for a in assignments]}, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting assignments: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_assignment_by_id(assignment_id):
        """Get a specific assignment by ID"""
        try:
            assignment = Assignment.query.get(assignment_id)
            
            if not assignment:
                return {'error': 'Penugasan tidak ditemukan'}, 404
                
            return {'assignment': assignment.to_dict()}, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting assignment {assignment_id}: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def create_assignment(data, admin_id):
        """Create a new assignment"""
        try:
            # Validasi data
            required_fields = ['officer_id', 'report_id']
            for field in required_fields:
                if not data.get(field):
                    return {'error': f'{field} diperlukan'}, 400
            
            # Check if officer exists
            officer = User.query.get(data['officer_id'])
            if not officer:
                return {'error': 'Officer tidak ditemukan'}, 404
            
            # Create assignment object
            assignment = Assignment(
                report_id=data['report_id'],
                officer_id=data['officer_id'],
                assigned_by=admin_id,
                status='PENDING',
                notes=data.get('notes')
            )
            
            db.session.add(assignment)
            db.session.commit()
            
            logger.logger.info(f"New assignment created: {assignment.id} for officer {assignment.officer_id}")
            
            return {'message': 'Penugasan berhasil dibuat', 'assignment': assignment.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error creating assignment: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def update_assignment(assignment_id, data, user_id):
        """Update an assignment"""
        try:
            assignment = Assignment.query.get(assignment_id)
            
            if not assignment:
                return {'error': 'Penugasan tidak ditemukan'}, 404
            
            # Check permissions - officer can only update status, admin can update everything
            is_admin = assignment.assigned_by == user_id
            is_officer = assignment.officer_id == user_id
            
            if not (is_admin or is_officer):
                logger.logger.warning(f"User {user_id} attempted to update assignment {assignment_id} without permission")
                return {'error': 'Anda tidak memiliki izin untuk mengupdate penugasan ini'}, 403
            
            # Determine which fields can be updated based on role
            if is_admin:
                updatable_fields = ['notes', 'status']
            else:  # is officer
                updatable_fields = ['status']
            
            for field in updatable_fields:
                if field in data:
                    setattr(assignment, field, data[field])
            
            # Track response time for status changes
            if is_officer and data.get('status') == 'ACCEPTED' and assignment.status != 'ACCEPTED':
                now = datetime.utcnow()
                created = assignment.created_at
                # Response time in seconds
                assignment.response_time = int((now - created).total_seconds())
            
            assignment.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.logger.info(f"Assignment updated: {assignment.id}, status: {assignment.status}")
            
            return {'message': 'Penugasan berhasil diupdate', 'assignment': assignment.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error updating assignment {assignment_id}: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def delete_assignment(assignment_id, user_id):
        """Delete an assignment"""
        try:
            assignment = Assignment.query.get(assignment_id)
            
            if not assignment:
                return {'error': 'Penugasan tidak ditemukan'}, 404
            
            # Only admin who created the assignment can delete it
            if assignment.assigned_by != user_id:
                logger.logger.warning(f"User {user_id} attempted to delete assignment {assignment_id} created by {assignment.assigned_by}")
                return {'error': 'Anda tidak memiliki izin untuk menghapus penugasan ini'}, 403
            
            db.session.delete(assignment)
            db.session.commit()
            
            logger.logger.info(f"Assignment deleted: {assignment.id}")
            
            return {'message': 'Penugasan berhasil dihapus'}, 200
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error deleting assignment {assignment_id}: {e}")
            return {'error': str(e)}, 500 