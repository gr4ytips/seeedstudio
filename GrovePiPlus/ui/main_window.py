# ui/main_window.py
import os
import sys
import time # Import time for time.sleep
from PyQt5.QtWidgets import QMainWindow, QTabWidget, QVBoxLayout, QWidget, QLabel, QApplication, QSizePolicy # Added QApplication, QSizePolicy
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from ui.dashboard_tab import DashboardTab
from ui.environment_sensors_tab import EnvironmentSensorsTab
from ui.basic_analog_sensors_tab import BasicAnalogSensorsTab
from ui.interactive_control_sensors_tab import InteractiveControlSensorsTab
from ui.weather_tab import WeatherTab
from ui.settings_tab import SettingsTab
from ui.ui_customization_tab import UICustomizationTab
from ui.plots_tab import PlotsTab # Import the new PlotsTab

from sensors.grovepi_sensor_manager import GrovePiSensorManager
from utils.logger import Logger
from utils.config_manager import ConfigManager
from utils.storage_monitor import StorageMonitor

class SensorWorker(QThread):
    """
    Worker thread to continuously read sensor data without blocking the UI.
    Emits signals with sensor readings.
    """
    sensor_data_updated = pyqtSignal(dict)
    dht_data_updated = pyqtSignal(float, float) # Temperature, Humidity
    ultrasonic_data_updated = pyqtSignal(float) # Distance in cm
    sound_data_updated = pyqtSignal(int) # Raw analog value
    light_data_updated = pyqtSignal(int) # Raw analog value
    button_data_updated = pyqtSignal(int) # 0 or 1
    rotary_angle_data_updated = pyqtSignal(int) # Raw analog value

    def __init__(self, sensor_manager, config_manager, read_interval=2): # Added config_manager
        super().__init__()
        self.sensor_manager = sensor_manager
        self.config = config_manager # Store config manager
        self.read_interval = read_interval
        self.running = True
        self.logger = Logger.get_logger()

    def run(self):
        """
        Main loop for the sensor worker thread. Reads sensors and emits signals.
        """
        self.logger.info("SensorWorker started.")
        while self.running:
            sensor_data = {}
            
            # DHT Sensor
            temp, hum = self.sensor_manager.read_dht_sensor()
            sensor_data["temperature"] = temp
            sensor_data["humidity"] = hum
            self.dht_data_updated.emit(temp, hum)

            # Ultrasonic Sensor
            ultrasonic_distance = self.sensor_manager.read_ultrasonic_sensor()
            sensor_data["ultrasonic"] = ultrasonic_distance
            self.ultrasonic_data_updated.emit(ultrasonic_distance)

            # Sound Sensor
            sound_value = self.sensor_manager.read_sound_sensor()
            sensor_data["sound"] = sound_value
            self.sound_data_updated.emit(sound_value)

            # Light Sensor
            light_value = self.sensor_manager.read_light_sensor()
            sensor_data["light"] = light_value
            self.light_data_updated.emit(light_value)

            # Button Sensor
            button_state = self.sensor_manager.read_button_sensor()
            sensor_data["button"] = button_state
            self.button_data_updated.emit(button_state)

            # Rotary Angle Sensor
            rotary_angle_value = self.sensor_manager.read_rotary_angle_sensor()
            sensor_data["rotary_angle"] = rotary_angle_value
            self.rotary_angle_data_updated.emit(rotary_angle_value)
            
            # Emit combined data for DashboardTab and logging
            self.sensor_data_updated.emit(sensor_data)

            # Log data if enabled
            if self.config.get_setting("enable_sensor_logging", True):
                self.sensor_manager.log_sensor_data(sensor_data)
            
            time.sleep(self.read_interval)
        self.logger.info("SensorWorker stopped.")

    def stop(self):
        """Stops the sensor worker thread."""
        self.running = False


class MainWindow(QMainWindow):
    """
    The main application window, managing tabs and sensor data updates.
    """
    def __init__(self, MOCK_SENSORS=False):
        super().__init__()
        self.config = ConfigManager.get_instance()
        
        # Initialize logger as early as possible
        Logger.initialize(
            debug_to_console=self.config.get_setting("enable_debug_to_console", True),
            debug_to_file=self.config.get_setting("enable_debug_to_file", True),
            log_dir=self.config.get_setting("log_directory", "Debug_Logs")
        )
        self.logger = Logger.get_logger()
        self.logger.info("Initializing Main Window...")

        self.storage_monitor = StorageMonitor()

        self.setWindowTitle("GrovePi+ Sensor Dashboard")
        self.setWindowIcon(QIcon(os.path.join(project_root, 'icons', 'app_icon.png'))) # Set your application icon

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)

        self.tabs = QTabWidget()
        # Ensure the QTabWidget expands to fill the available space
        self.tabs.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.main_layout.addWidget(self.tabs)

        self.sensor_manager = GrovePiSensorManager(mock_sensors=MOCK_SENSORS)
        
        # Order of initialization is crucial:
        # 1. Setup Tabs - this creates instances of all tab widgets (which the worker will connect to)
        self._setup_tabs() # This creates self.dashboard_tab, self.settings_tab, etc.

        # 2. Setup Sensor Worker - now it can safely be created and its signals will be connected later
        self._setup_sensor_worker() # This creates self.sensor_worker

        # 3. Now that both self.sensor_worker and all tabs exist, connect all signals.
        self._connect_signals()

        # 4. Setup System Monitor
        self._setup_system_monitor()

        self._apply_theme(self.config.get_setting("current_theme", "dark_theme"))
        self.logger.info("Main Window initialized.")

    def _setup_tabs(self):
        """
        Initializes and adds all application tabs.
        Does NOT connect signals here, as connections happen in _connect_signals().
        """
        # Dashboard tab
        self.dashboard_tab = DashboardTab(self.sensor_manager, parent=self) # Pass self as parent
        self.tabs.addTab(self.dashboard_tab, "Dashboard")

        # Environment Sensors tab
        self.environment_sensors_tab = EnvironmentSensorsTab(self.sensor_manager, parent=self)
        self.tabs.addTab(self.environment_sensors_tab, "Environment Sensors")

        # Basic Analog Sensors tab
        self.basic_analog_sensors_tab = BasicAnalogSensorsTab(self.sensor_manager, parent=self)
        self.tabs.addTab(self.basic_analog_sensors_tab, "Basic Analog Sensors")

        # Interactive Control Sensors tab
        self.interactive_control_sensors_tab = InteractiveControlSensorsTab(self.sensor_manager, parent=self)
        self.tabs.addTab(self.interactive_control_sensors_tab, "Interactive Controls")

        # Weather tab
        self.weather_tab = WeatherTab(parent=self) # WeatherTab doesn't need sensor_manager
        self.tabs.addTab(self.weather_tab, "Weather")

        # Plots tab
        self.plots_tab = PlotsTab(self.config, parent=self) # PlotsTab already takes config
        self.tabs.addTab(self.plots_tab, "Plots")

        # Settings tab
        self.settings_tab = SettingsTab(self.config, self.sensor_manager, self.storage_monitor, parent=self)
        self.tabs.addTab(self.settings_tab, "Settings")

        # UI Customization tab
        self.ui_customization_tab = UICustomizationTab(self, parent=self) # Pass self (MainWindow) as reference
        self.tabs.addTab(self.ui_customization_tab, "UI Customization")

    def _setup_sensor_worker(self):
        """Sets up the worker thread for continuous sensor reading."""
        read_interval = self.config.get_setting("sensor_read_interval", 2)
        # Pass self.config to the SensorWorker
        self.sensor_worker = SensorWorker(self.sensor_manager, self.config, read_interval) 
        # Worker is started here, but signals are connected in _connect_signals
        self.sensor_worker.start()
        self.logger.info("SensorWorker thread started.")

    def _connect_signals(self):
        """Connects all signals between various components after they are initialized."""
        # Connections from sensor_worker to respective tabs
        self.sensor_worker.sensor_data_updated.connect(self.dashboard_tab.update_sensor_data)
        self.sensor_worker.dht_data_updated.connect(self.environment_sensors_tab.update_dht_data)
        self.sensor_worker.ultrasonic_data_updated.connect(self.basic_analog_sensors_tab.update_ultrasonic_data)
        self.sensor_worker.sound_data_updated.connect(self.basic_analog_sensors_tab.update_sound_data)
        self.sensor_worker.light_data_updated.connect(self.basic_analog_sensors_tab.update_light_data)
        self.sensor_worker.button_data_updated.connect(self.interactive_control_sensors_tab.update_button_status)
        self.sensor_worker.rotary_angle_data_updated.connect(self.interactive_control_sensors_tab.update_rotary_angle_data)

        # Connections for theme changes
        self.ui_customization_tab.theme_changed.connect(self._apply_theme)
        # Connect the new sensor_display_type_changed signal
        self.ui_customization_tab.sensor_display_type_changed.connect(self._update_sensor_display_style)

        # Connections from settings_tab to other components
        # Changed _fetch_and_update_weather to fetch_and_update_weather (public method)
        self.settings_tab.settings_updated.connect(self.weather_tab.fetch_and_update_weather) 
        self.settings_tab.settings_updated.connect(self.sensor_worker.stop) # Stop worker to apply new interval
        self.settings_tab.settings_updated.connect(self._restart_sensor_worker) # Restart with new interval
        self.settings_tab.settings_updated.connect(self.plots_tab._apply_theme_colors_to_plot) # In case theme changed
        
        # Connect sensor manager relay and LED bar signals to interactive controls tab
        self.sensor_manager.relay_status_changed.connect(self.interactive_control_sensors_tab.update_relay_status)
        self.sensor_manager.led_bar_status_changed.connect(self.interactive_control_sensors_tab.update_led_bar_status)
        
        # Also connect to dashboard for relay/LED bar updates (These methods will be added to DashboardTab next)
        self.sensor_manager.relay_status_changed.connect(self.dashboard_tab.update_relay_status)
        self.sensor_manager.led_bar_status_changed.connect(self.dashboard_tab.update_led_bar_status)

    def _restart_sensor_worker(self):
        """Restarts the sensor worker with updated settings (e.g., read interval)."""
        if self.sensor_worker.isRunning():
            self.sensor_worker.stop()
            self.sensor_worker.wait() # Wait for the thread to finish cleanly
        
        # Re-initialize worker with new interval from config
        new_read_interval = self.config.get_setting("sensor_read_interval", 2)
        self.sensor_worker = SensorWorker(self.sensor_manager, self.config, new_read_interval) # Pass self.config

        # Reconnect signals for the new worker instance
        # It's important to re-establish these connections as the old worker is gone
        self.sensor_worker.sensor_data_updated.connect(self.dashboard_tab.update_sensor_data)
        self.sensor_worker.dht_data_updated.connect(self.environment_sensors_tab.update_dht_data)
        self.sensor_worker.ultrasonic_data_updated.connect(self.basic_analog_sensors_tab.update_ultrasonic_data)
        self.sensor_worker.sound_data_updated.connect(self.basic_analog_sensors_tab.update_sound_data)
        self.sensor_worker.light_data_updated.connect(self.basic_analog_sensors_tab.update_light_data)
        self.sensor_worker.button_data_updated.connect(self.interactive_control_sensors_tab.update_button_status)
        self.sensor_worker.rotary_angle_data_updated.connect(self.interactive_control_sensors_tab.update_rotary_angle_data)

        self.sensor_worker.start()
        self.logger.info("SensorWorker thread restarted with new interval: {}s.".format(new_read_interval))

    def _update_sensor_display_style(self):
        """
        Calls the _create_gauges method on relevant tabs to redraw gauges
        with the newly selected display type.
        """
        self.logger.info("Updating sensor display style for relevant tabs.")
        # Re-create gauges in EnvironmentSensorsTab
        self.environment_sensors_tab._create_gauges()
        self.basic_analog_sensors_tab._create_gauges()
        self.interactive_control_sensors_tab._create_gauges() # Assuming it also has gauges affected by this.
        # DashboardTab needs to be updated too if it uses these gauges directly
        self.dashboard_tab._create_gauges() # Assuming it also has gauges affected by this.


    def _setup_system_monitor(self):
        """Sets up a timer for periodic system status checks (e.g., disk space)."""
        self.system_monitor_timer = QTimer(self)
        self.system_monitor_timer.timeout.connect(self._check_system_status)
        interval_ms = self.config.get_setting("system_check_interval_ms", 60000) # Default 1 minute
        self.system_monitor_timer.start(interval_ms)
        self.logger.info("System monitor started with interval: {}ms.".format(interval_ms))
        self._check_system_status() # Initial check

    def _check_system_status(self):
        """Checks system parameters like disk space and logs warnings/critical messages."""
        self.logger.debug("Performing system status check.")
        
        # Get project root for relative paths
        project_root_abs = os.path.abspath(os.path.join(script_dir, os.pardir))

        # Check debug log directory space
        log_dir = self.config.get_setting("log_directory", "Debug_Logs")
        log_abs_path = os.path.join(project_root_abs, log_dir)
        free_space_log_gb = self.storage_monitor.get_free_space_gb(log_abs_path)
        if free_space_log_gb < self.config.get_setting("min_free_space_gb", 1.0):
            self.logger.warning("Low disk space in log directory ({}): {:.2f} GB available.".format(log_abs_path, free_space_log_gb))

        # Check archive directory space
        archive_dir = self.config.get_setting("archive_directory", "Archive_Sensor_Logs")
        archive_abs_path = os.path.join(project_root_abs, archive_dir)
        free_space_archive_gb = self.storage_monitor.get_free_space_gb(archive_abs_path)
        if free_space_archive_gb < self.config.get_setting("min_free_space_gb", 1.0):
            self.logger.warning("Low disk space in archive directory ({}): {:.2f} GB available.".format(archive_abs_path, free_space_archive_gb))
            if free_space_archive_gb < 0.1: # Very critical threshold
                self.config.set_setting("enable_archive", False)
                self.logger.critical("Extremely low disk space. Disabling archiving.")

        # Check sensor log directory space
        sensor_log_dir = self.config.get_setting("sensor_log_directory", "Sensor_Logs")
        sensor_log_abs_path = os.path.join(project_root_abs, sensor_log_dir)
        free_space_sensor_log_gb = self.storage_monitor.get_free_space_gb(sensor_log_abs_path)
        if free_space_sensor_log_gb < self.config.get_setting("min_free_space_gb", 1.0):
            self.logger.warning("Low disk space in sensor log directory ({}): {:.2f} GB available.".format(sensor_log_abs_path, free_space_sensor_log_gb))
            if free_space_sensor_log_gb < 0.1: # Very critical threshold
                self.config.set_setting("enable_sensor_logging", False)
                self.logger.critical("Extremely low disk space. Disabling sensor CSV logging.")


    def closeEvent(self, event):
        """
        Handles the close event for the main window, stopping the sensor thread.
        """
        self.logger.info("Main Window closing. Stopping sensor worker...")
        if self.sensor_worker.isRunning():
            self.sensor_worker.stop()
            self.sensor_worker.wait() # Wait for the thread to finish
        self.logger.info("Sensor worker stopped. Application exiting.")
        event.accept()

    def _apply_theme(self, theme_name):
        """
        Applies the selected theme stylesheet to the application.
        :param theme_name: The name of the theme (e.g., "dark_theme", "light_theme").
        """
        self.logger.info("Applying theme: {}".format(theme_name))
        theme_path = os.path.join(project_root, 'themes', "{}.qss".format(theme_name))
        
        if os.path.exists(theme_path):
            try:
                with open(theme_path, "r") as f:
                    self.setStyleSheet(f.read())
                self.config.set_setting("current_theme", theme_name) # Save the applied theme
                self.logger.info("Theme '{}' applied successfully.".format(theme_name))
                
                # Manually trigger style updates for custom widgets that don't auto-update
                # This is crucial for GaugeWidget and LEDBarWidget which draw custom elements.
                for tab_idx in range(self.tabs.count()):
                    tab = self.tabs.widget(tab_idx)
                    if hasattr(tab, 'set_style'):
                        tab.set_style()
                    
                    # For custom widgets within tabs, call their _set_theme_colors method
                    # (assuming they have one, like GaugeWidget does).
                    # This might require iterating over specific widgets.
                    # For now, we'll call set_style on tabs which then should propagate.
                    # Explicitly call _set_theme_colors on gauge widgets within dashboard
                    if isinstance(tab, DashboardTab):
                        self.dashboard_tab._set_theme_colors_for_gauges()
                    if isinstance(tab, EnvironmentSensorsTab):
                        self.environment_sensors_tab._set_theme_colors()
                    if isinstance(tab, BasicAnalogSensorsTab):
                        self.basic_analog_sensors_tab._set_theme_colors()
                    if isinstance(tab, InteractiveControlSensorsTab):
                        self.interactive_control_sensors_tab._set_theme_colors()
                    if isinstance(tab, WeatherTab):
                        # WeatherTab handles its own theme colors through _set_theme_colors
                        tab._set_theme_colors() # Update internal QColors for dynamic elements
                        # Changed _fetch_and_update_weather to fetch_and_update_weather (public method)
                        if hasattr(tab, 'fetch_and_update_weather'):
                            tab.fetch_and_update_weather() 
                        else:
                            self.logger.warning("WeatherTab does not have 'fetch_and_update_weather' method.")
                    if isinstance(tab, PlotsTab):
                        tab._apply_theme_colors_to_plot()


            except Exception as e:
                self.logger.error("Error applying theme '{}': {}".format(theme_name, e))
        else:
            self.logger.warning("Theme file not found: {}".format(theme_path))

