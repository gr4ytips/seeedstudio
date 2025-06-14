# utils/logger.py
import logging
import logging.handlers
import os
from datetime import datetime
import sys # Import the sys module

class Logger:
    """
    Manages application logging to console and a rotating file.
    Singleton pattern to ensure only one logger instance.
    """
    _instance = None
    _is_initialized = False

    @staticmethod
    def initialize(debug_to_console=True, debug_to_file=True, log_dir="Debug_Logs", max_bytes=10*1024*1024, backup_count=5):
        """
        Initializes the logger. Should be called once at application startup.
        :param debug_to_console: True to log debug messages to console.
        :param debug_to_file: True to log debug messages to a file.
        :param log_dir: Directory to store log files.
        :param max_bytes: Maximum size of log file before rotation (bytes).
        :param backup_count: Number of backup log files to keep.
        """
        if Logger._is_initialized:
            # If already initialized, we might want to reconfigure or just return
            # For simplicity, if it's already initialized, we assume settings were set.
            # A more advanced logger might reconfigure existing handlers here.
            # For this app, main_window ensures it's called once.
            return

        Logger._instance = logging.getLogger("SensorApp")
        Logger._instance.setLevel(logging.DEBUG) # Lowest level for full capture

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        # Clear existing handlers to prevent duplicate logs if initialize is called multiple times
        if Logger._instance.handlers:
            for handler in Logger._instance.handlers:
                handler.close()
            Logger._instance.handlers = []

        # Console Handler
        if debug_to_console:
            console_handler = logging.StreamHandler(sys.stdout) # Explicitly use stdout
            console_handler.setLevel(logging.INFO) # Console typically INFO or higher
            console_handler.setFormatter(formatter)
            Logger._instance.addHandler(console_handler)

        # File Handler with rotation
        if debug_to_file:
            # Resolve log_dir relative to the project root
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
            full_log_dir_path = os.path.join(project_root, log_dir)

            if not os.path.exists(full_log_dir_path):
                os.makedirs(full_log_dir_path)
            
            log_file_path = os.path.join(full_log_dir_path, "app_debug.log")
            
            file_handler = logging.handlers.RotatingFileHandler(
                log_file_path,
                maxBytes=max_bytes,      # 10 MB per file
                backupCount=backup_count # Keep 5 backup files
            )
            file_handler.setLevel(logging.DEBUG)
            file_handler.setFormatter(formatter)
            Logger._instance.addHandler(file_handler)

        Logger._is_initialized = True
        Logger._instance.info("Logger initialized.")

    @staticmethod
    def get_logger():
        """
        Returns the initialized logger instance.
        Raises an error if logger is not initialized.
        """
        if not Logger._is_initialized:
            # Fallback for cases where get_logger might be called before explicit init
            # In the main app flow, main_window will always ensure it's initialized.
            Logger.initialize() 
        return Logger._instance

# Example usage (for testing, will be removed in final structure)
if __name__ == "__main__":
    # Initialize with custom settings
    Logger.initialize(debug_to_console=True, debug_to_file=True, log_dir="Test_Logs", max_bytes=10000, backup_count=2)
    logger = Logger.get_logger()

    logger.debug("This is a debug message.")
    logger.info("This is an info message.")
    logger.warning("This is a warning message.")
    logger.error("This is an error message.")
    logger.critical("This is a critical message.")

    # Simulate some logging to trigger rotation if maxBytes is low
    for i in range(100):
        logger.info("Log entry number {}".format(i))

    # Test getting logger without explicit init (should still work if initialized once)
    another_logger = Logger.get_logger()
    another_logger.info("Another logger instance test.")

    # Clean up test logs (optional)
    # import shutil
    # if os.path.exists("Test_Logs"):
    #     shutil.rmtree("Test_Logs")
