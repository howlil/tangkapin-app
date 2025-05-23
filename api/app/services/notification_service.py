from pusher import Pusher
from app import db
from app.models import Notification, User
from datetime import datetime, timedelta
from sqlalchemy.exc import SQLAlchemyError
from config import Config
from app.utils.logger import logger
import requests
import json

class NotificationService:
    def __init__(self):
        self.pusher = Pusher(
            app_id=Config.PUSHER_APP_ID,
            key=Config.PUSHER_KEY,
            secret=Config.PUSHER_SECRET,
            cluster=Config.PUSHER_CLUSTER,
            ssl=True
        )
        logger.logger.info(f"Pusher client initialized - Cluster: {Config.PUSHER_CLUSTER}")
        
        # Firebase Cloud Messaging API URL
        self.fcm_url = "https://fcm.googleapis.com/fcm/send"
        # FCM API Key (in real app would be set in Config)
        self.fcm_api_key = Config.FCM_API_KEY if hasattr(Config, 'FCM_API_KEY') else None
        
    def create_notification(self, user_id, title, message, notification_type, reference_id=None):
        """Create notification in database"""
        try:
            notification = Notification(
                user_id=user_id,
                title=title,
                message=message,
                notification_type=notification_type,
                reference_id=reference_id,
                is_read=False
            )
            
            db.session.add(notification)
            db.session.commit()
            
            logger.logger.info(f"Notification created for user {user_id}: {title}")
            
            return notification
            
        except Exception as e:
            db.session.rollback()
            logger.logger.error(f"Error creating notification: {e}")
            return None
    
    def send_push_notification(self, user_ids, title, message, data=None):
        """Send push notification to user devices"""
        if not self.fcm_api_key:
            logger.logger.warning("FCM API Key not configured, skipping push notification")
            return False
        
        try:
            # Get FCM tokens for users
            users = User.query.filter(User.id.in_(user_ids)).all()
            fcm_tokens = [user.fcm_token for user in users if user.fcm_token]
            
            if not fcm_tokens:
                logger.logger.warning("No valid FCM tokens found for users")
                return False
            
            # Prepare notification payload
            payload = {
                "registration_ids": fcm_tokens,
                "notification": {
                    "title": title,
                    "body": message,
                    "sound": "default"
                }
            }
            
            # Add data payload if provided
            if data:
                payload["data"] = data
            
            # Send to FCM
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"key={self.fcm_api_key}"
            }
            
            response = requests.post(
                self.fcm_url,
                data=json.dumps(payload),
                headers=headers
            )
            
            if response.status_code == 200:
                result = response.json()
                success = result.get('success', 0)
                failure = result.get('failure', 0)
                logger.logger.info(f"Push notification sent: {success} success, {failure} failure")
                return True
            else:
                logger.logger.error(f"FCM error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.logger.error(f"Error sending push notification: {e}")
            return False
    
    def send_weapon_detection_alert(self, camera_id, report_id, weapon_type):
        """Send weapon detection alert to camera owner and admins"""
        try:
            from app.models import Camera
            
            # Get camera details
            camera = Camera.query.get(camera_id)
            if not camera:
                logger.logger.error(f"Camera {camera_id} not found")
                return False
            
            # Create notification for camera owner
            owner_notification = self.create_notification(
                user_id=camera.owner_id,
                title="🚨 DETEKSI SENJATA!",
                message=f"Sistem mendeteksi {weapon_type} di kamera {camera.name}. Mohon segera periksa.",
                notification_type="EMERGENCY",
                reference_id=report_id
            )
            
            # Get all admin users
            admins = User.query.filter_by(role='admin').all()
            admin_ids = [admin.id for admin in admins]
            
            # Create notifications for all admins
            for admin_id in admin_ids:
                admin_notification = self.create_notification(
                    user_id=admin_id,
                    title="🚨 DETEKSI SENJATA!",
                    message=f"Sistem mendeteksi {weapon_type} di kamera {camera.name}. Mohon segera verifikasi.",
                    notification_type="EMERGENCY",
                    reference_id=report_id
                )
            
            # Send push notifications
            all_recipients = [camera.owner_id] + admin_ids
            
            self.send_push_notification(
                user_ids=all_recipients,
                title="🚨 DETEKSI SENJATA!",
                message=f"Sistem mendeteksi {weapon_type} di lokasi {camera.name}.",
                data={
                    "type": "weapon_detection",
                    "report_id": report_id,
                    "camera_id": camera_id
                }
            )
            
            logger.logger.info(f"Weapon detection alerts sent for camera {camera_id}")
            return True
            
        except Exception as e:
            logger.logger.error(f"Error sending weapon detection alert: {e}")
            return False
    
    def send_assignment_notification(self, assignment_id, officer_id):
        """Send assignment notification to officer"""
        try:
            from app.models import Assignment
            
            # Get assignment details
            assignment = Assignment.query.get(assignment_id)
            if not assignment:
                logger.logger.error(f"Assignment {assignment_id} not found")
                return False
            
            # Create notification for officer
            officer_notification = self.create_notification(
                user_id=officer_id,
                title="📋 Penugasan Baru",
                message="Anda mendapat penugasan baru. Mohon segera konfirmasi.",
                notification_type="ASSIGNMENT",
                reference_id=assignment_id
            )
            
            # Send push notification
            self.send_push_notification(
                user_ids=[officer_id],
                title="📋 Penugasan Baru",
                message="Anda mendapat penugasan baru. Mohon segera konfirmasi.",
                data={
                    "type": "new_assignment",
                    "assignment_id": assignment_id,
                    "report_id": assignment.report_id
                }
            )
            
            logger.logger.info(f"Assignment notification sent to officer {officer_id}")
            return True
            
        except Exception as e:
            logger.logger.error(f"Error sending assignment notification: {e}")
            return False
    
    def send_admin_alert(self, report_id, camera_id, alert_type, message):
        """Send alert to all admin users"""
        try:
            # Get all admin users
            admins = User.query.filter_by(role='admin').all()
            admin_ids = [admin.id for admin in admins]
            
            if not admin_ids:
                logger.logger.warning("No admin users found for alert")
                return False
            
            # Create notifications for all admins
            for admin_id in admin_ids:
                admin_notification = self.create_notification(
                    user_id=admin_id,
                    title="🔔 Sistem Keamanan",
                    message=message,
                    notification_type=alert_type.upper(),
                    reference_id=report_id
                )
            
            # Send push notifications
            self.send_push_notification(
                user_ids=admin_ids,
                title="🔔 Sistem Keamanan",
                message=message,
                data={
                    "type": alert_type,
                    "report_id": report_id,
                    "camera_id": camera_id
                }
            )
            
            logger.logger.info(f"Admin alert sent to {len(admin_ids)} admins")
            return True
            
        except Exception as e:
            logger.logger.error(f"Error sending admin alert: {e}")
            return False
    
    def send_system_alert(self, alert_data, users_to_notify=None):
        """Send system alert to specified users or all users"""
        try:
            title = alert_data.get('title', '🔔 Sistem Notifikasi')
            message = alert_data.get('message', 'Pemberitahuan sistem')
            priority = alert_data.get('priority', 'medium')
            
            # If no specific users, notify all active users
            if not users_to_notify:
                users = User.query.filter_by(is_active=True).all()
                users_to_notify = [user.id for user in users]
            
            notification_type = 'SYSTEM'
            if priority.lower() == 'high':
                notification_type = 'SYSTEM_URGENT'
                title = '⚠️ ' + title
            
            # Create notifications for all users
            notifications = []
            for user_id in users_to_notify:
                notification = self.create_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type
                )
                notifications.append(notification)
            
            # Send push notification for high priority
            if priority.lower() in ['high', 'urgent']:
                self.send_push_notification(
                    user_ids=users_to_notify,
                    title=title,
                    message=message,
                    data={"type": "system_alert", "priority": priority}
                )
            
            logger.logger.info(f"System alert sent to {len(users_to_notify)} users")
            
            # Return first notification for method consistency
            return notifications[0] if notifications else None
            
        except Exception as e:
            logger.logger.error(f"Error sending system alert: {e}")
            return None
    
    def _send_pusher_notification(self, user_id, notification_id, notification_data):
        """Send notification via Pusher to a specific user"""
        try:
            # Send via Pusher to user's private channel
            self.pusher.trigger(
                f'private-user-{user_id}',
                'new-notification',
                notification_data
            )
            
            logger.logger.info(f"Pusher notification sent to user {user_id}")
            return True
            
        except Exception as e:
            # Update notification status to failed
            try:
                notification = Notification.query.get(notification_id)
                if notification:
                    notification.status = 'failed'
                    notification.retry_count += 1
                    notification.last_retry = datetime.now()
                    db.session.commit()
            except SQLAlchemyError:
                pass
                
            logger.logger.error(f"Failed to send Pusher notification: {e}")
            return False
    
    def send_emergency_alert(self, emergency_data):
        """Send emergency alert to all active users"""
        try:
            # Get all active users
            active_users = User.query.filter_by(is_active=True).all()
            
            # Create notification in database
            notification = Notification(
                type='emergency',
                title=emergency_data.get('title', 'EMERGENCY ALERT'),
                message=emergency_data.get('message', 'Emergency situation detected'),
                data=emergency_data,
                priority='critical',
                status='sent',
                recipients=[user.id for user in active_users]
            )
            
            db.session.add(notification)
            db.session.commit()
            
            # Broadcast to all users channel
            self.pusher.trigger(
                'presence-emergency-channel',
                'emergency-alert',
                {
                    'id': notification.id,
                    'type': 'emergency',
                    'title': notification.title,
                    'message': notification.message,
                    'emergency_data': emergency_data,
                    'timestamp': notification.created_at.isoformat(),
                    'sound': emergency_data.get('sound', True)
                }
            )
            
            # Also send to individual channels in case they're not subscribed to presence channel
            for user in active_users:
                self._send_pusher_notification(
                    user_id=user.id,
                    notification_id=notification.id,
                    notification_data={
                        'id': notification.id,
                        'type': 'emergency',
                        'title': notification.title,
                        'message': notification.message,
                        'emergency_data': emergency_data,
                        'timestamp': notification.created_at.isoformat(),
                        'sound': emergency_data.get('sound', True)
                    }
                )
            
            logger.logger.info(f"Emergency alert broadcasted to {len(active_users)} users")
            return notification
            
        except Exception as e:
            logger.logger.error(f"Error broadcasting emergency alert: {e}")
            return None
    
    def retry_failed_notifications(self):
        """Retry sending failed notifications"""
        try:
            # Get failed notifications that haven't exceeded retry limit
            failed_notifications = Notification.query.filter_by(
                status='failed'
            ).filter(
                Notification.retry_count < Config.MAX_NOTIFICATION_RETRIES
            ).all()
            
            results = []
            for notification in failed_notifications:
                logger.logger.info(f"Retrying notification {notification.id} (attempt {notification.retry_count + 1})")
                
                # Retry sending to each recipient
                for user_id in notification.recipients:
                    success = self._send_pusher_notification(
                        user_id=user_id,
                        notification_id=notification.id,
                        notification_data=notification.data
                    )
                    
                    if success:
                        notification.status = 'sent'
                        results.append({'id': notification.id, 'success': True})
                    else:
                        results.append({'id': notification.id, 'success': False})
                
                notification.retry_count += 1
                notification.last_retry = datetime.now()
                db.session.commit()
                
            return results
            
        except Exception as e:
            logger.logger.error(f"Error retrying failed notifications: {e}")
            return []
    
    def get_notification_queue_status(self):
        """Get status of notification queue (metrics for monitoring)"""
        try:
            # Calculate notification metrics
            total_count = Notification.query.count()
            failed_count = Notification.query.filter_by(status='failed').count()
            sent_count = Notification.query.filter_by(status='sent').count()
            read_count = Notification.query.filter_by(status='read').count()
            
            # Get notifications by priority
            critical_count = Notification.query.filter_by(priority='critical').count()
            high_count = Notification.query.filter_by(priority='high').count()
            medium_count = Notification.query.filter_by(priority='medium').count()
            low_count = Notification.query.filter_by(priority='low').count()
            
            return {
                'total': total_count,
                'sent': sent_count,
                'failed': failed_count,
                'read': read_count,
                'by_priority': {
                    'critical': critical_count,
                    'high': high_count,
                    'medium': medium_count,
                    'low': low_count
                }
            }
        except Exception as e:
            logger.logger.error(f"Error getting notification queue status: {e}")
            return {
                'error': str(e)
            }
    
    def mark_notification_as_read(self, notification_id, user_id):
        """Mark notification as read for specific user"""
        try:
            notification = Notification.query.get(notification_id)
            
            if not notification:
                return {
                    'success': False,
                    'message': 'Notification not found'
                }
                
            # Check if user is a recipient
            if user_id not in notification.recipients:
                return {
                    'success': False,
                    'message': 'User is not a recipient of this notification'
                }
                
            # If we're tracking read status per-user
            if not notification.read_by:
                notification.read_by = []
            
            if user_id not in notification.read_by:
                notification.read_by.append(user_id)
            
            # If all recipients have read, mark notification as read
            if set(notification.read_by) >= set(notification.recipients):
                notification.status = 'read'
            
            db.session.commit()
            
            return {
                'success': True,
                'notification_id': notification.id
            }
            
        except Exception as e:
            logger.logger.error(f"Error marking notification as read: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def send_bulk_notifications(self, notifications):
        """Send multiple notifications in bulk"""
        try:
            created_notifications = []
            sent_count = 0
            
            for notification_data in notifications:
                notification = Notification(
                    type=notification_data.get('type', 'general'),
                    title=notification_data.get('title', 'Notification'),
                    message=notification_data.get('message', ''),
                    data=notification_data.get('data', {}),
                    priority=notification_data.get('priority', 'medium'),
                    status='pending',
                    recipients=notification_data.get('recipients', [])
                )
                
                db.session.add(notification)
                db.session.commit()
                
                # Send via Pusher to each recipient
                success = True
                for user_id in notification.recipients:
                    result = self._send_pusher_notification(
                        user_id=user_id,
                        notification_id=notification.id,
                        notification_data={
                            'id': notification.id,
                            'type': notification.type,
                            'title': notification.title,
                            'message': notification.message,
                            'data': notification.data,
                            'timestamp': notification.created_at.isoformat()
                        }
                    )
                    
                    if not result:
                        success = False
                
                notification.status = 'sent' if success else 'failed'
                db.session.commit()
                
                if success:
                    sent_count += 1
                
                created_notifications.append(notification)
            
            logger.logger.info(f"Bulk notifications sent: {sent_count}/{len(notifications)}")
            return {
                'success': True,
                'sent_count': sent_count,
                'total_count': len(notifications)
            }
            
        except Exception as e:
            logger.logger.error(f"Error sending bulk notifications: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cleanup_old_notifications(self, days_old=30):
        """Clean up old notifications to prevent DB bloat"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Get notifications older than cutoff date
            old_notifications = Notification.query.filter(
                Notification.created_at < cutoff_date
            ).all()
            
            deleted_count = len(old_notifications)
            
            # Delete them
            for notification in old_notifications:
                db.session.delete(notification)
            
            db.session.commit()
            logger.logger.info(f"Cleaned up {deleted_count} old notifications")
            return deleted_count
            
        except Exception as e:
            logger.logger.error(f"Error cleaning up notifications: {e}")
            return 0