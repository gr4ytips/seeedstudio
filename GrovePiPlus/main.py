# main.py
import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from PyQt5.QtWidgets import QApplication
from ui.main_window import MainWindow
from utils.config_manager import ConfigManager # Import ConfigManager

# --- IMPORTANT CONFIGURATION ---
# Set to True to use mocked sensor data (for development without GrovePi)
# Set to False to use actual GrovePi sensors (requires GrovePi connected)
# Now reads from configuration, with True as a default if not set
MOCK_SENSORS = ConfigManager.get_instance().get_setting("enable_mock_sensors", True)
# -------------------------------

def main():
    """
    Main function to initialize and run the Sensor App.
    """
    app = QApplication(sys.argv)
    
    # Create the main window instance
    main_window = MainWindow(MOCK_SENSORS=MOCK_SENSORS)
    
    # Show the main window maximized
    main_window.showMaximized()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
