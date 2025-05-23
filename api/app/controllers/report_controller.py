from app.models import Report, db
from app.utils.logger import logger
from datetime import datetime

class ReportController:
    @staticmethod
    def get_all_reports(user_id=None, status=None):
        """Get all reports, optionally filtered by reporter_id or status"""
        try:
            query = Report.query
            
            if user_id:
                query = query.filter_by(reporter_id=user_id)
                
            if status:
                query = query.filter_by(status=status)
                
            # Sort by most recent first
            query = query.order_by(Report.created_at.desc())
            
            reports = query.all()
            return {'reports': [r.to_dict() for r in reports]}, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting reports: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_report_by_id(report_id):
        """Get a specific report by ID"""
        try:
            report = Report.query.get(report_id)
            
            if not report:
                return {'error': 'Laporan tidak ditemukan'}, 404
                
            return {'report': report.to_dict()}, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting report {report_id}: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def create_report(data, reporter_id):
        """Create a new report"""
        try:
            # Validasi data
            required_fields = ['title', 'camera_id']
            for field in required_fields:
                if not data.get(field):
                    return {'error': f'{field} diperlukan'}, 400
            
            # Create report object
            report = Report(
                title=data['title'],
                description=data.get('description'),
                camera_id=data['camera_id'],
                reporter_id=reporter_id,
                priority=data.get('priority', 'MEDIUM'),
                weapon_type=data.get('weapon_type'),
                detection_confidence=data.get('detection_confidence'),
                detection_image_url=data.get('detection_image_url'),
                is_automatic=data.get('is_automatic', False)
            )
            
            db.session.add(report)
            db.session.commit()
            
            logger.logger.info(f"New report created: {report.title} (ID: {report.id})")
            
            return {'message': 'Laporan berhasil dibuat', 'report': report.to_dict()}, 201
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error creating report: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def update_report(report_id, data, user_id):
        """Update a report"""
        try:
            report = Report.query.get(report_id)
            
            if not report:
                return {'error': 'Laporan tidak ditemukan'}, 404
            
            # Only reporter or admin can update
            # This check would be more sophisticated in a real app
            if report.reporter_id != user_id:
                logger.logger.warning(f"User {user_id} attempted to update report {report_id} created by {report.reporter_id}")
                return {'error': 'Anda tidak memiliki izin untuk mengupdate laporan ini'}, 403
            
            # Update fields
            updatable_fields = ['title', 'description', 'priority', 'status']
            
            for field in updatable_fields:
                if field in data:
                    setattr(report, field, data[field])
            
            report.updated_at = datetime.utcnow()
            db.session.commit()
            
            logger.logger.info(f"Report updated: {report.title} (ID: {report.id})")
            
            return {'message': 'Laporan berhasil diupdate', 'report': report.to_dict()}, 200
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error updating report {report_id}: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def delete_report(report_id, user_id):
        """Delete a report"""
        try:
            report = Report.query.get(report_id)
            
            if not report:
                return {'error': 'Laporan tidak ditemukan'}, 404
            
            # Only reporter or admin can delete
            if report.reporter_id != user_id:
                logger.logger.warning(f"User {user_id} attempted to delete report {report_id} created by {report.reporter_id}")
                return {'error': 'Anda tidak memiliki izin untuk menghapus laporan ini'}, 403
            
            db.session.delete(report)
            db.session.commit()
            
            logger.logger.info(f"Report deleted: {report.title} (ID: {report.id})")
            
            return {'message': 'Laporan berhasil dihapus'}, 200
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error deleting report {report_id}: {e}")
            return {'error': str(e)}, 500 