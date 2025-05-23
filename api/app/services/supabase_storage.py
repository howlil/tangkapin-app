import os
import uuid
from datetime import datetime
from supabase import create_client, Client
from config import Config
import cv2
import numpy as np
from PIL import Image
import io
from app.utils.logger import logger

class SupabaseStorageService:
    def __init__(self):
        self.supabase: Client = create_client(
            Config.SUPABASE_URL, 
            Config.SUPABASE_SERVICE_KEY  # Use service key for storage operations
        )
        
        # Storage buckets
        self.detection_bucket = Config.DETECTION_IMAGES_BUCKET
        self.evidence_bucket = Config.EVIDENCE_BUCKET
        
        # Initialize buckets if not exists
        self._initialize_buckets()
    
    def _initialize_buckets(self):
        """Initialize storage buckets if they don't exist"""
        try:
            # Create detection images bucket
            try:
                self.supabase.storage.create_bucket(self.detection_bucket, {"public": True})
                logger.logger.info(f"Created bucket: {self.detection_bucket}")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.logger.warning(f"Detection bucket error: {e}")
            
            # Create evidence files bucket
            try:
                self.supabase.storage.create_bucket(self.evidence_bucket, {"public": True})
                logger.logger.info(f"Created bucket: {self.evidence_bucket}")
            except Exception as e:
                if "already exists" not in str(e).lower():
                    logger.logger.warning(f"Evidence bucket error: {e}")
                    
        except Exception as e:
            logger.logger.error(f"Error initializing buckets: {e}")
    
    def upload_detection_image(self, cv2_image, camera_id, weapon_type=None):
        """Upload detection image dari CV2 ke Supabase Storage"""
        try:
            # Generate filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"detection_{camera_id}_{timestamp}_{str(uuid.uuid4())[:8]}.jpg"
            filepath = f"cameras/{camera_id}/{filename}"
            
            # Convert CV2 image to bytes
            _, buffer = cv2.imencode('.jpg', cv2_image, [cv2.IMWRITE_JPEG_QUALITY, 90])
            image_bytes = buffer.tobytes()
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_(self.detection_bucket).upload(
                path=filepath,
                file=image_bytes,
                file_options={
                    "content-type": "image/jpeg",
                    "x-upsert": "true"  # Allow overwrite
                }
            )
            
            if result:
                # Get public URL
                public_url = self.get_public_url(self.detection_bucket, filepath)
                
                logger.logger.info(f"Detection image uploaded: {filename}")
                return {
                    'success': True,
                    'filename': filename,
                    'filepath': filepath,
                    'public_url': public_url,
                    'bucket': self.detection_bucket
                }
            else:
                raise Exception("Upload failed - no result returned")
                
        except Exception as e:
            logger.logger.error(f"Error uploading detection image: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': None,
                'public_url': None
            }
    
    def upload_evidence_file(self, file_data, file_type, report_id, description=None):
        """Upload evidence file ke Supabase Storage"""
        try:
            # Generate filename berdasarkan type
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            
            # Determine file extension
            file_extensions = {
                'image': 'jpg',
                'video': 'mp4', 
                'audio': 'mp3',
                'document': 'pdf'
            }
            
            ext = file_extensions.get(file_type, 'bin')
            filename = f"evidence_{report_id}_{timestamp}_{str(uuid.uuid4())[:8]}.{ext}"
            filepath = f"reports/{report_id}/{filename}"
            
            # Set content type
            content_types = {
                'image': 'image/jpeg',
                'video': 'video/mp4',
                'audio': 'audio/mpeg',
                'document': 'application/pdf'
            }
            content_type = content_types.get(file_type, 'application/octet-stream')
            
            # Upload to Supabase Storage
            result = self.supabase.storage.from_(self.evidence_bucket).upload(
                path=filepath,
                file=file_data,
                file_options={
                    "content-type": content_type,
                    "x-upsert": "true"
                }
            )
            
            if result:
                # Get public URL
                public_url = self.get_public_url(self.evidence_bucket, filepath)
                
                logger.logger.info(f"Evidence file uploaded: {filename}")
                return {
                    'success': True,
                    'filename': filename,
                    'filepath': filepath,
                    'public_url': public_url,
                    'bucket': self.evidence_bucket,
                    'file_type': file_type
                }
            else:
                raise Exception("Upload failed - no result returned")
                
        except Exception as e:
            logger.logger.error(f"Error uploading evidence file: {e}")
            return {
                'success': False,
                'error': str(e),
                'filename': None,
                'public_url': None
            }
    
    def get_public_url(self, bucket_name, filepath):
        """Get public URL untuk file di Supabase Storage"""
        try:
            result = self.supabase.storage.from_(bucket_name).get_public_url(filepath)
            return result
        except Exception as e:
            logger.logger.error(f"Error getting public URL: {e}")
            return None
    
    def delete_file(self, bucket_name, filepath):
        """Delete file dari Supabase Storage"""
        try:
            result = self.supabase.storage.from_(bucket_name).remove([filepath])
            
            if result:
                logger.logger.info(f"File deleted: {filepath}")
                return True
            else:
                logger.logger.warning(f"File not found or already deleted: {filepath}")
                return False
                
        except Exception as e:
            logger.logger.error(f"Error deleting file: {e}")
            return False
    
    def generate_signed_url(self, bucket_name, filepath, expires_in=3600):
        """Generate signed URL untuk private access"""
        try:
            result = self.supabase.storage.from_(bucket_name).create_signed_url(
                path=filepath,
                expires_in=expires_in  # seconds
            )
            
            if result and 'signedURL' in result:
                return result['signedURL']
            else:
                return None
                
        except Exception as e:
            logger.logger.error(f"Error generating signed URL: {e}")
            return None
    
    def list_files(self, bucket_name, folder_path=""):
        """List files dalam bucket/folder"""
        try:
            result = self.supabase.storage.from_(bucket_name).list(folder_path)
            
            files = []
            if result:
                for item in result:
                    files.append({
                        'name': item.get('name'),
                        'size': item.get('metadata', {}).get('size'),
                        'created_at': item.get('created_at'),
                        'updated_at': item.get('updated_at'),
                        'content_type': item.get('metadata', {}).get('mimetype')
                    })
            
            return files
            
        except Exception as e:
            logger.logger.error(f"Error listing files: {e}")
            return []
    
    def upload_from_base64(self, base64_data, bucket_name, filepath, content_type="image/jpeg"):
        """Upload file dari base64 string ke Supabase Storage"""
        try:
            # Strip potential data URL prefix
            if "base64," in base64_data:
                base64_data = base64_data.split("base64,")[1]
            
            # Convert base64 to bytes
            import base64
            file_bytes = base64.b64decode(base64_data)
            
            # Upload file
            result = self.supabase.storage.from_(bucket_name).upload(
                path=filepath,
                file=file_bytes,
                file_options={
                    "content-type": content_type,
                    "x-upsert": "true"
                }
            )
            
            if result:
                public_url = self.get_public_url(bucket_name, filepath)
                return {
                    'success': True,
                    'filepath': filepath,
                    'public_url': public_url
                }
            else:
                return {
                    'success': False,
                    'error': 'Upload failed'
                }
        except Exception as e:
            logger.logger.error(f"Error uploading from base64: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_bucket_info(self, bucket_name):
        """Get information about a storage bucket"""
        try:
            buckets = self.supabase.storage.list_buckets()
            for bucket in buckets:
                if bucket.get('name') == bucket_name:
                    return bucket
            return None
        except Exception as e:
            logger.logger.error(f"Error getting bucket info: {e}")
            return None
    
    def cleanup_old_files(self, bucket_name, days_old=30):
        """Clean up files older than specified days"""
        try:
            # Get all files in the bucket
            all_files = self.list_files(bucket_name, "")
            if not all_files:
                return 0
            
            # Calculate cutoff date
            from datetime import timedelta
            cutoff_date = datetime.now() - timedelta(days=days_old)
            
            # Parse dates from filenames and delete old files
            deleted_count = 0
            for file_obj in all_files:
                try:
                    file_path = file_obj.get('name')
                    # Try to extract date from filename (format: YYYYMMDD)
                    date_part = file_path.split('_')[1] if '_' in file_path else None
                    
                    if date_part and len(date_part) >= 8:
                        try:
                            file_date = datetime.strptime(date_part[:8], "%Y%m%d")
                            if file_date < cutoff_date:
                                self.delete_file(bucket_name, file_path)
                                deleted_count += 1
                        except ValueError:
                            # If date can't be parsed from filename, skip
                            continue
                except:
                    continue
                    
            return deleted_count
        except Exception as e:
            logger.logger.error(f"Error cleaning up old files: {e}")
            return 0