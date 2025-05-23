from app.models import User, Camera, Report, Assignment, db
from app.utils.logger import logger
from app.services.notification_service import NotificationService
# from app.services.background_tasks import BackgroundTaskManager  # Comment this to avoid circular import
from datetime import datetime, timedelta
import os
import sys

class SystemController:
    @staticmethod
    def get_system_status():
        """Get system status"""
        try:
            # Check database connection
            try:
                db.session.execute('SELECT 1')
                db_status = "healthy"
            except:
                db_status = "error"
            
            # Get application metrics
            user_count = User.query.count()
            camera_count = Camera.query.filter_by(is_active=True).count()
            online_cameras = Camera.query.filter_by(is_active=True, status='online').count()
            
            # Get memory usage
            import psutil
            process = psutil.Process(os.getpid())
            memory_usage = process.memory_info().rss / 1024 / 1024  # in MB
            
            return {
                'status': 'healthy' if db_status == 'healthy' else 'degraded',
                'timestamp': datetime.utcnow().isoformat(),
                'uptime': "Unknown",  # Would be implemented in a real app
                'components': {
                    'database': db_status,
                    'storage': 'healthy',
                    'background_tasks': 'healthy'
                },
                'metrics': {
                    'users': user_count,
                    'cameras': {
                        'total': camera_count,
                        'online': online_cameras
                    },
                    'memory_usage_mb': round(memory_usage, 2)
                }
            }, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting system status: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_system_metrics():
        """Get detailed system metrics"""
        try:
            now = datetime.utcnow()
            one_day_ago = now - timedelta(days=1)
            one_week_ago = now - timedelta(days=7)
            
            # User metrics
            total_users = User.query.count()
            active_users = User.query.filter_by(is_active=True).count()
            
            # Camera metrics
            total_cameras = Camera.query.count()
            online_cameras = Camera.query.filter_by(status='online').count()
            
            # Report metrics
            reports_today = Report.query.filter(Report.created_at >= one_day_ago).count()
            reports_week = Report.query.filter(Report.created_at >= one_week_ago).count()
            
            # Assignment metrics
            pending_assignments = Assignment.query.filter_by(status='PENDING').count()
            completed_assignments = Assignment.query.filter_by(status='COMPLETED').count()
            
            # Response time metrics (average in minutes)
            assignments_with_time = Assignment.query.filter(
                Assignment.response_time.isnot(None)
            ).all()
            
            avg_response_time = 0
            if assignments_with_time:
                total_time = sum(a.response_time for a in assignments_with_time)
                avg_response_time = round(total_time / len(assignments_with_time) / 60, 2)
            
            return {
                'timestamp': now.isoformat(),
                'users': {
                    'total': total_users,
                    'active': active_users
                },
                'cameras': {
                    'total': total_cameras,
                    'online': online_cameras,
                    'offline': total_cameras - online_cameras
                },
                'reports': {
                    'today': reports_today,
                    'this_week': reports_week,
                    'total': Report.query.count()
                },
                'assignments': {
                    'pending': pending_assignments,
                    'completed': completed_assignments,
                    'total': Assignment.query.count()
                },
                'performance': {
                    'avg_response_time_mins': avg_response_time
                }
            }, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting system metrics: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def create_backup():
        """Create system backup (simulation)"""
        try:
            # In a real app, this would create an actual backup
            # For now, just simulate the process
            
            timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
            backup_name = f"tangkapin_backup_{timestamp}.zip"
            
            logger.logger.info(f"System backup initiated: {backup_name}")
            
            return {
                'message': 'Backup berhasil dimulai',
                'backup_name': backup_name,
                'status': 'processing',
                'timestamp': datetime.utcnow().isoformat()
            }, 202
            
        except Exception as e:
            logger.logger.error(f"Error creating backup: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def get_logs(lines=100):
        """Get system logs"""
        try:
            logs = []
            log_file = os.path.join('logs', 'tangkapin.log')
            
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    logs = f.readlines()[-lines:]  # Get last N lines
            
            return {
                'logs': logs,
                'count': len(logs)
            }, 200
            
        except Exception as e:
            logger.logger.error(f"Error getting logs: {e}")
            return {'error': str(e)}, 500
    
    @staticmethod
    def send_test_notification(user_id):
        """Send test notification"""
        try:
            notification_service = NotificationService()
            
            notification = notification_service.send_system_alert(
                alert_data={
                    'title': 'Test Notification',
                    'message': 'This is a test notification from the system',
                    'priority': 'low'
                },
                users_to_notify=[user_id]
            )
            
            if notification:
                logger.logger.info(f"Test notification sent to user {user_id}")
                return {
                    'message': 'Notifikasi test berhasil dikirim',
                    'notification_id': notification.id
                }, 200
            else:
                return {'error': 'Gagal mengirim notifikasi'}, 500
            
        except Exception as e:
            logger.logger.error(f"Error sending test notification: {e}")
            return {'error': str(e)}, 500 