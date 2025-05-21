# config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Database Configuration
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_size": 10,
        "pool_timeout": 30,
        "max_overflow": 20,
        "pool_pre_ping": True,
        "pool_recycle": 300
    }

    # JWT Configuration
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-secret-key-change-in-production")
    JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRES = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES", 3600 * 24))  # 24 hours

    # Flask Configuration
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    FLASK_ENV = os.getenv("FLASK_ENV", "development")
    DEBUG = FLASK_ENV == "development"

    # CORS Configuration
    CORS_HEADERS = "Content-Type"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",")

    # File Upload Configuration
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 16 * 1024 * 1024))  # 16MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'mp4', 'avi', 'mov', 'pdf', 'doc', 'docx'}

    # Pusher Configuration (for real-time notifications)
    PUSHER_APP_ID = os.getenv("PUSHER_APP_ID")
    PUSHER_KEY = os.getenv("PUSHER_KEY")
    PUSHER_SECRET = os.getenv("PUSHER_SECRET")
    PUSHER_CLUSTER = os.getenv("PUSHER_CLUSTER", "ap1")
    PUSHER_SSL = os.getenv("PUSHER_SSL", "true").lower() == "true"

    # Supabase Configuration (for file storage)
    SUPABASE_URL = os.getenv("SUPABASE_URL")
    SUPABASE_KEY = os.getenv("SUPABASE_KEY")
    SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "tangkapin-storage")

 
    # CCTV Configuration
    CCTV_DEFAULT_TIMEOUT = int(os.getenv("CCTV_DEFAULT_TIMEOUT", 10))
    CCTV_STREAM_TIMEOUT = int(os.getenv("CCTV_STREAM_TIMEOUT", 30))

    # ML Model Configuration
    ML_MODEL_PATH = os.getenv("ML_MODEL_PATH", "app/models/best.pt")
    ML_CONFIDENCE_THRESHOLD = float(os.getenv("ML_CONFIDENCE_THRESHOLD", 0.7))
    ML_DETECTION_INTERVAL = int(os.getenv("ML_DETECTION_INTERVAL", 5))  # seconds



    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO" if not DEBUG else "DEBUG")
    LOG_FILE = os.getenv("LOG_FILE", "logs/app.log")
    LOG_MAX_BYTES = int(os.getenv("LOG_MAX_BYTES", 10 * 1024 * 1024))  # 10MB
    LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", 5))

    # Application Configuration
    APP_NAME = os.getenv("APP_NAME", "TangkapIn")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")
    API_VERSION = os.getenv("API_VERSION", "v1")

    # Security Configuration
    BCRYPT_LOG_ROUNDS = int(os.getenv("BCRYPT_LOG_ROUNDS", 13))
    PASSWORD_MIN_LENGTH = int(os.getenv("PASSWORD_MIN_LENGTH", 8))
    
    # Rate Limiting
    RATELIMIT_DEFAULT = os.getenv("RATELIMIT_DEFAULT", "100 per hour")

    # Pagination
    DEFAULT_PAGE_SIZE = int(os.getenv("DEFAULT_PAGE_SIZE", 20))
    MAX_PAGE_SIZE = int(os.getenv("MAX_PAGE_SIZE", 100))

    @staticmethod
    def init_app(app):
        """Initialize application with this config"""
        pass

class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_LEVEL = "DEBUG"

class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False
    SQLALCHEMY_ECHO = False
    LOG_LEVEL = "WARNING"
    
    # Production security settings
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Testing configuration"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv("TEST_DATABASE_URL", "sqlite:///test.db")
    WTF_CSRF_ENABLED = False
    LOG_LEVEL = "DEBUG"

# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': DevelopmentConfig
}