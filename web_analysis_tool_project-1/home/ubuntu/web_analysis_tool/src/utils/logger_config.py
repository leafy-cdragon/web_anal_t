# logger_config.py

import logging
import os
from logging.handlers import RotatingFileHandler

# Define the path for log files within the application's data directory
APP_NAME = "WebAnalysisTool"
# On Linux, typical user data dir might be ~/.local/share/APP_NAME or ~/.config/APP_NAME
# For simplicity in this sandboxed environment, we use a directory in the project structure or user's home.
# This should be consistent with where other app data (like GPG home) might be stored.
APP_DATA_DIR = os.path.join(os.path.expanduser("~"), ".web_analysis_tool_data")
LOG_DIR = os.path.join(APP_DATA_DIR, "logs")

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE_PATH = os.path.join(LOG_DIR, "app.log")

def setup_logging(log_level=logging.INFO):
    """
    Configures centralized logging for the application.
    Logs to both console and a rotating file.
    """
    # Get the root logger
    logger = logging.getLogger() # Root logger
    logger.setLevel(log_level) # Set the minimum level for the root logger

    # Prevent multiple handlers if setup_logging is called more than once (e.g., in tests or reloads)
    if logger.hasHandlers():
        logger.handlers.clear()

    # Formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(module)s.%(funcName)s:%(lineno)d - %(message)s'
    )

    # Console Handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # File Handler (Rotating)
    # Rotates logs when they reach 2MB, keeps up to 5 backup logs.
    file_handler = RotatingFileHandler(
        LOG_FILE_PATH, maxBytes=2*1024*1024, backupCount=5, encoding=\'utf-8\'
    )
    file_handler.setLevel(log_level) # Log everything at INFO level and above to file
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    logging.info("Logging configured. Log file: %s", LOG_FILE_PATH)

    # Return the root logger if needed, though usually modules will get their own logger via logging.getLogger(__name__)
    return logger

# Call setup_logging here to configure it once when this module is imported.
# However, it's often better to call this explicitly from the main application entry point.
# For this project structure, we'll assume main_app.py will call it.

# Example of how other modules would get a logger:
# import logging
# logger = logging.getLogger(__name__)
# logger.info("This is a test message from another module.")

