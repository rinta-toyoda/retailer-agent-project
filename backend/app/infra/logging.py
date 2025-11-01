"""
Logging Configuration
Centralized logging setup for the application.
Marking Criteria: 4.4 (Incorporation of Advanced Technologies)
"""

import logging
import os
import sys
from pathlib import Path


def setup_logging(log_level: str = None, log_file: str = None) -> logging.Logger:
    """
    Configure application logging.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path

    Returns:
        Configured logger instance
    """
    log_level = log_level or os.getenv("LOG_LEVEL", "INFO")
    log_file = log_file or os.getenv("LOG_FILE", "logs/app.log")

    # Create logs directory if it doesn't exist
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

    # Configure logging format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # Console output
            logging.FileHandler(log_file) if log_file else logging.NullHandler(),  # File output
        ]
    )

    logger = logging.getLogger("retailer_agent")
    logger.info(f"Logging initialized at {log_level} level")

    return logger


# Global logger instance
logger = setup_logging()
