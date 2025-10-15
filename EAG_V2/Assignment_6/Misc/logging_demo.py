"""
Logging Demo
This script demonstrates basic Python logging functionality.
"""

import logging

# Configure the root logger with INFO level
# This sets the minimum severity level that will be logged (DEBUG < INFO < WARNING < ERROR < CRITICAL)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Create a logger instance for this module
# Using __name__ ensures the logger is named after the module for better organization
logger = logging.getLogger(__name__)

# Log messages at different severity levels
logger.debug("This is a debug message")
logger.info("This is an info message")
logger.warning("This is a warning message")
logger.error("This is an error message")
logger.critical("This is a critical message")