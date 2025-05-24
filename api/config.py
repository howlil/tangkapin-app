import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'tangkapin-secret-key-dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # JWT Configuration
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret-string'
    JWT_ACCESS_TOKEN_EXPIRES = False  # Token tidak expire otomatis
    
    # Pusher Configuration
    PUSHER_APP_ID = "1911283"
    PUSHER_KEY = "ef6ded14f456b73f9a12"
    PUSHER_SECRET = "275efadb307fd2df90b7"
    PUSHER_CLUSTER = "ap1"
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY')
    SUPABASE_SERVICE_KEY = os.environ.get('SUPABASE_SERVICE_KEY')  # For storage operations
    
    SUPABASE_STORAGE_BUCKET = 'foto-maling'  
    DETECTION_IMAGES_BUCKET = 'detection-images'  
    EVIDENCE_BUCKET = 'evidence-files' 
    
    # ML Detection Configuration
    ML_MODEL_PATH = os.path.join(os.getcwd(),'app' 'ml_models', 'best.pt')
    DETECTION_CONFIDENCE_THRESHOLD = 0.7  # 70% confidence minimum
    
    # Notification Configuration
    NOTIFICATION_RETRY_ATTEMPTS = 3
    NOTIFICATION_QUEUE_SIZE = 1000