# utils/storage_monitor.py
import os
import sys

# Add SensorApp root to path to ensure utils can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.logger import Logger

class StorageMonitor:
    """
    Provides methods to check disk storage space.
    """
    def __init__(self):
        self.logger = Logger.get_logger()

    def get_free_space_gb(self, path):
        """
        Gets the free space in gigabytes for a given path.
        Works on Unix-like systems (Raspberry Pi OS).
        
        :param path: The directory path to check.
        :return: Free space in GB, or 0.0 if an error occurs.
        """
        if not os.path.exists(path):
            self.logger.warning("Path for storage check does not exist: {}".format(path))
            return 0.0
            
        try:
            # os.statvfs is Unix-specific and available on Raspberry Pi OS
            stat = os.statvfs(path)
            free_bytes = stat.f_bavail * stat.f_frsize # Available blocks * fragment size
            free_gb = free_bytes / (1024.0 * 1024.0 * 1024.0)
            return free_gb
        except Exception as e:
            self.logger.error("Error checking disk space for {}: {}".format(path, e))
            return 0.0

# Example usage (for testing)
if __name__ == "__main__":
    Logger.initialize(debug_to_console=True)
    monitor = StorageMonitor()

    # Check current directory
    current_dir_free = monitor.get_free_space_gb(".")
    print("Free space in current directory: {:.2f} GB".format(current_dir_free))

    # Check root directory
    root_dir_free = monitor.get_free_space_gb("/")
    print("Free space in root directory: {:.2f} GB".format(root_dir_free))

    # Check a non-existent path
    non_existent_path = "/this/path/does/not/exist_12345"
    non_existent_free = monitor.get_free_space_gb(non_existent_path)
    print("Free space in non-existent path '{}': {:.2f} GB".format(non_existent_path, non_existent_free))

