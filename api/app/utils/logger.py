import os
import logging
from logging.handlers import RotatingFileHandler
import time
import traceback
from flask import request, g
import sys

class Logger:
    def __init__(self, app=None):
        self.app = app
        self.logger = logging.getLogger('tangkapin')
        
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.app = app
        
        # Get configuration from app
        log_dir = app.config.get('LOG_DIRECTORY', 'logs')
        log_level_name = app.config.get('LOG_LEVEL', 'INFO')
        log_max_size = app.config.get('LOG_MAX_SIZE', 10 * 1024 * 1024)  # 10MB
        log_backup_count = app.config.get('LOG_BACKUP_COUNT', 10)
        
        # Map string log level to logging constant
        log_level = getattr(logging, log_level_name.upper(), logging.INFO)
        
        # Create logs directory if it doesn't exist
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configure logger
        self.logger.setLevel(log_level)
        
        # Clear any existing handlers
        if self.logger.handlers:
            self.logger.handlers.clear()
        
        # Set up file handler with rotation
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, 'tangkapin.log'),
            maxBytes=log_max_size,
            backupCount=log_backup_count
        )
        
        # Set format for handlers
        formatter = logging.Formatter(
            '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        
        # Set up console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(log_level)
        
        # Add handlers to logger
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        
        # Register request logger
        app.before_request(self._log_request_start)
        app.after_request(self._log_request_end)
        
        # Register error logger
        app.register_error_handler(Exception, self._log_exception)
        
        # Make logger available in app context
        app.logger = self.logger
        
        self.logger.info('Logger initialized with level: %s', log_level_name)
    
    def _log_request_start(self):
        g.start_time = time.time()
        self.logger.info(f"Request started: {request.method} {request.path}")
    
    def _log_request_end(self, response):
        if hasattr(g, 'start_time'):
            elapsed_time = time.time() - g.start_time
            self.logger.info(
                f"Request completed: {request.method} {request.path} "
                f"- Status: {response.status_code} - Duration: {elapsed_time:.4f}s"
            )
        return response
    
    def _log_exception(self, exception):
        self.logger.error(f"Exception on {request.path}: {str(exception)}\n{traceback.format_exc()}")
        return {"error": "Internal server error"}, 500

# Create a global logger instance
logger = Logger() 