"""
Utility functions for logging and common operations
"""

import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None, level: int = logging.INFO) -> logging.Logger:
    """
    Get a configured logger instance
    
    Args:
        name: Logger name (defaults to calling module)
        level: Logging level
        
    Returns:
        Configured logger instance
    """
    logger_name = name or __name__
    logger = logging.getLogger(logger_name)
    
    if not logger.handlers:
        # Create console handler
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        # Add handler to logger
        logger.addHandler(handler)
        logger.setLevel(level)
    
    return logger
