"""
Logging Configuration - Kayos Cloud Licensing
Centralized logging setup for development and production
"""

import logging
import sys
from pathlib import Path


def setup_logging():
    """Setup comprehensive logging configuration"""
    
    # Create logs directory
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # Configure root logger
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # File handler
            logging.FileHandler('logs/kayos_licensing.log', encoding='utf-8'),
            # Console handler
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Set specific levels for libraries
    logging.getLogger('uvicorn').setLevel(logging.WARNING)
    logging.getLogger('sqlalchemy').setLevel(logging.WARNING)


def get_logger(name: str) -> logging.Logger:
    """Get logger with given name"""
    return logging.getLogger(name)
