import logging
from flask import current_app
import os

def setup_logger(name):
    """
    Setup a logger for a specific module
    
    Args:
        name (str): The name of the logger
        
    Returns:
        logging.Logger: The configured logger
    """
    logger = logging.getLogger(name)
    
    # Skip if handler already exists
    if logger.handlers:
        return logger
    
    # Set level based on app config or default to INFO
    try:
        log_level = current_app.config.get('LOG_LEVEL', 'INFO').upper()
    except RuntimeError:
        # Not in app context, use INFO as default
        log_level = 'INFO'
    
    # Set logger level
    logger.setLevel(getattr(logging, log_level))
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Add file handler if in app context and LOG_FILE is defined
    try:
        log_file = current_app.config.get('LOG_FILE')
        if log_file:
            # Create log directory if it doesn't exist
            log_dir = os.path.dirname(log_file)
            if not os.path.exists(log_dir):
                os.makedirs(log_dir)
            
            # Create file handler
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)
    except RuntimeError:
        # Not in app context, skip file handler
        pass
    
    return logger