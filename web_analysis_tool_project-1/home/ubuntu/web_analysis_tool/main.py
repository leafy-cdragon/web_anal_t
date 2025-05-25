# main.py (Entry point for the Web Analysis Tool)

import sys
import os
import logging

# Ensure the src directory is in the Python path if main.py is in src
# If main.py is one level above src, this might need adjustment or be handled by how it's run.
# Assuming main.py is in the root of the project, and imports are like `from src.gui...`
# For the current structure where main_app.py is in src/gui, we might call that directly
# or create a launcher script.

# Let's assume this main.py is at the root of `web_analysis_tool` for simplicity of launching.
# To make this work, we need to adjust sys.path or ensure modules are packaged.
# A simpler approach for now is to make this a launcher that cds into src and runs main_app.py

# Path adjustments to allow imports from src.utils, src.gui etc.
# This assumes main.py is in the root of the web_analysis_tool project directory.
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(project_root, "src"))

from src.gui.main_app import WebAnalysisToolGUI, QApplication
from src.utils.logger_config import setup_logging, LOG_DIR, APP_DATA_DIR
from src.utils.custom_exceptions import ConfigurationError

if __name__ == "__main__":
    # Create application data directories if they don't exist
    # This ensures log directory and GPG home parent directory are created before use.
    if not os.path.exists(APP_DATA_DIR):
        os.makedirs(APP_DATA_DIR, exist_ok=True)
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR, exist_ok=True)

    # Setup centralized logging
    # The log level can be configured here (e.g., logging.DEBUG for more verbose output)
    logger = setup_logging(log_level=logging.INFO)
    logger.info("Application starting...")

    # GPG Home for the application (consistent with PGPManager and main_app.py)
    gpg_home_path = os.path.join(APP_DATA_DIR, "gnupg_home")
    logger.info(f"Application GPG home directory set to: {gpg_home_path}")
    # PGPManager will create it if it doesn't exist, with 0o700 permissions.

    try:
        app = QApplication(sys.argv)
        # Optional: Set an application icon
        # icon_path = os.path.join(project_root, "src", "gui", "icon.png") # Assuming you have an icon.png
        # if os.path.exists(icon_path):
        #     app.setWindowIcon(QIcon(icon_path))

        # Initialize and show the main application window
        # Pass the gpg_home_path to the GUI, so it can pass it to PGPManager
        # The main_app.py was already designed to construct this path, so this is more of a confirmation.
        main_window = WebAnalysisToolGUI() # main_app.py already calculates gpg_home_path
        main_window.show()
        logger.info("Main application window displayed.")
        sys.exit(app.exec())

    except ConfigurationError as e:
        logger.critical(f"Configuration error on startup: {e}. Application cannot start.")
        # In a real app, you might show a GUI error message here if QApplication is already running
        # For now, logging is the primary feedback for this type of early error.
        sys.exit(1)
    except ImportError as e:
        logger.critical(f"ImportError on startup: {e}. Ensure all dependencies are installed and paths are correct.")
        # This often means a module is missing or PYTHONPATH is not set up correctly.
        sys.exit(1)
    except Exception as e:
        logger.critical(f"An unexpected critical error occurred on startup: {e}", exc_info=True)
        sys.exit(1)
    finally:
        logger.info("Application shutting down.")

