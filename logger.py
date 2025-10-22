import logging
import sys
from config import Config

def setup_logger():
    """Setup application logging"""
    
    # Create logger
    logger = logging.getLogger("proofforge")
    logger.setLevel(getattr(logging, Config.LOG_LEVEL.upper()))
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    
    # Add handler to logger
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger

# Global logger instance
logger = setup_logger()
