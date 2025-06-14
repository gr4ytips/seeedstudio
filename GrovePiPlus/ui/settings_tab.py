# ui/settings_tab.py
import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGroupBox, QFormLayout, QCheckBox, QLineEdit, QPushButton, QHBoxLayout, QFileDialog, QMessageBox, QScrollArea, QSizePolicy
from PyQt5.QtCore import Qt, pyqtSignal # Import pyqtSignal
from PyQt5.QtGui import QFont, QColor

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.logger import Logger
from utils.config_manager import ConfigManager
from utils.storage_monitor import StorageMonitor

class SettingsTab(QWidget):
    """
    Separate tab for application settings:
    - Debug messages
    - Archive and Log directories
    - Weather API Key and Location
    - Mock/Live Sensor Mode
    """
    settings_updated = pyqtSignal() # Define a signal that indicates settings have been updated

    def __init__(self, config_manager, sensor_manager, storage_monitor, parent=None):
        super(SettingsTab, self).__init__(parent)
        self.logger = Logger.get_logger()
        self.config = config_manager
        self.sensor_manager = sensor_manager
        self.storage_monitor = storage_monitor

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        
        self._set_theme_colors() # Set initial theme colors for dynamic elements
        self._setup_ui()
        self.set_style() # Apply QSS for static elements
        self.logger.info("SettingsTab initialized.")

    def _set_theme_colors(self):
        """Sets internal color attributes based on the current theme for dynamic elements."""
        current_theme = self.config.get_setting("current_theme", "dark_theme")

        # Define color palettes for various themes
        theme_palettes = {
            "dark_theme": {
                "normal_text": QColor("#abb2bf"), # Light gray
                "warning_text": QColor("#FF4500"), # OrangeRed
                "success_text": QColor("#7CFC00"), # LimeGreen
                "group_box_border": QColor("#555"),
                "group_box_bg": QColor("rgba(40, 40, 40, 0.7)"),
                "group_box_title": QColor("#61afef"), # Blue for titles
                "checkbox_color": QColor("#EEE"),
                "checkbox_indicator_unchecked_bg": QColor("#444444"), # Dark gray for unchecked
                "checkbox_indicator_checked_bg": QColor("#61afef"),   # Blue for checked
                "checkbox_indicator_border": QColor("#777777"),    # Medium gray border
                "line_edit_bg": QColor("#333"),
                "line_edit_text": QColor("#EEE"),
                "line_edit_border": QColor("#666"),
                "button_bg": QColor("#1E90FF"), # DodgerBlue
                "button_hover_bg": QColor("#1C86EE"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#333"), # Dark gray for scrollbar trough
                "scrollbar_handle": QColor("#61afef"), # Blue for scrollbar handle
                "scrollbar_button": QColor("#1E90FF"), # DodgerBlue for scrollbar buttons
            },
            "light_theme": {
                "normal_text": QColor("#333333"),
                "warning_text": QColor("#FF4500"),
                "success_text": QColor("#28A745"), # Green
                "group_box_border": QColor("#ccc"),
                "group_box_bg": QColor("rgba(255, 255, 255, 0.9)"),
                "group_box_title": QColor("#007bff"),
                "checkbox_color": QColor("#333333"),
                "checkbox_indicator_unchecked_bg": QColor("#E0E0E0"), # Light gray for unchecked
                "checkbox_indicator_checked_bg": QColor("#007bff"),   # Blue for checked
                "checkbox_indicator_border": QColor("#AAAAAA"),    # Medium gray border
                "line_edit_bg": QColor("#f8f8f8"),
                "line_edit_text": QColor("#333"),
                "line_edit_border": QColor("#ccc"),
                "button_bg": QColor("#007bff"),
                "button_hover_bg": QColor("#0056b3"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#f0f0f0"),
                "scrollbar_handle": QColor("#007bff"),
                "scrollbar_button": QColor("#007bff"),
            },
            "blue_theme": {
                "normal_text": QColor("#e0f2f7"),
                "warning_text": QColor("#FF6347"), # Tomato
                "success_text": QColor("#3CB371"), # MediumSeaGreen
                "group_box_border": QColor("#3c6595"),
                "group_box_bg": QColor("rgba(26, 42, 64, 0.7)"),
                "group_box_title": QColor("#87CEEB"),
                "checkbox_color": QColor("#e0f2f7"),
                "checkbox_indicator_unchecked_bg": QColor("#2b4a68"),
                "checkbox_indicator_checked_bg": QColor("#4682B4"),
                "checkbox_indicator_border": QColor("#5a7c9f"),
                "line_edit_bg": QColor("#223f5b"),
                "line_edit_text": QColor("#e0f2f7"),
                "line_edit_border": QColor("#4a6c8e"),
                "button_bg": QColor("#4682B4"),
                "button_hover_bg": QColor("#3a719d"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#2b4a68"),
                "scrollbar_handle": QColor("#4682B4"),
                "scrollbar_button": QColor("#4682B4"),
            },
            "dark_gray_theme": {
                "normal_text": QColor("#fdfdfd"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#3CB371"),
                "group_box_border": QColor("#666"),
                "group_box_bg": QColor("rgba(60, 63, 65, 0.7)"),
                "group_box_title": QColor("#79c0ff"),
                "checkbox_color": QColor("#fdfdfd"),
                "checkbox_indicator_unchecked_bg": QColor("#4b4f52"),
                "checkbox_indicator_checked_bg": QColor("#6a737d"),
                "checkbox_indicator_border": QColor("#888888"),
                "line_edit_bg": QColor("#4b4f52"),
                "line_edit_text": QColor("#fdfdfd"),
                "line_edit_border": QColor("#6c7072"),
                "button_bg": QColor("#6a737d"),
                "button_hover_bg": QColor("#586069"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#444"),
                "scrollbar_handle": QColor("#6a737d"),
                "scrollbar_button": QColor("#6a737d"),
            },
            "forest_green_theme": {
                "normal_text": QColor("#FFFFFF"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#9ACD32"), # YellowGreen
                "group_box_border": QColor("#66BB6A"),
                "group_box_bg": QColor("rgba(34, 139, 34, 0.7)"),
                "group_box_title": QColor("#A5D6A7"),
                "checkbox_color": QColor("#FFFFFF"),
                "checkbox_indicator_unchecked_bg": QColor("#339933"),
                "checkbox_indicator_checked_bg": QColor("#66BB6A"),
                "checkbox_indicator_border": QColor("#88CC88"),
                "line_edit_bg": QColor("#339933"),
                "line_edit_text": QColor("#FFFFFF"),
                "line_edit_border": QColor("#4CAF50"),
                "button_bg": QColor("#66BB6A"),
                "button_hover_bg": QColor("#4CAF50"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#388E3C"),
                "scrollbar_handle": QColor("#66BB6A"),
                "scrollbar_button": QColor("#66BB6A"),
            },
            "warm_sepia_theme": {
                "normal_text": QColor("#F5DEB3"), # Wheat
                "warning_text": QColor("#CD5C5C"), # IndianRed
                "success_text": QColor("#6B8E23"), # OliveDrab
                "group_box_border": QColor("#A0522D"),
                "group_box_bg": QColor("rgba(112, 66, 20, 0.7)"),
                "group_box_title": QColor("#DEB887"),
                "checkbox_color": QColor("#F5DEB3"),
                "checkbox_indicator_unchecked_bg": QColor("#7C4F2A"),
                "checkbox_indicator_checked_bg": QColor("#A0522D"),
                "checkbox_indicator_border": QColor("#C08040"),
                "line_edit_bg": QColor("#7C4F2A"),
                "line_edit_text": QColor("#F5DEB3"),
                "line_edit_border": QColor("#A0522D"),
                "button_bg": QColor("#A0522D"),
                "button_hover_bg": QColor("#8B4513"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#8B4513"),
                "scrollbar_handle": QColor("#A0522D"),
                "scrollbar_button": QColor("#A0522D"),
            },
            "ocean_blue_theme": {
                "normal_text": QColor("#E0FFFF"), # Light Cyan
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#66CDAA"), # MediumAquamarine
                "group_box_border": QColor("#0066CC"),
                "group_box_bg": QColor("rgba(0, 51, 102, 0.7)"),
                "group_box_title": QColor("#87CEEB"),
                "checkbox_color": QColor("#E0FFFF"),
                "checkbox_indicator_unchecked_bg": QColor("#004080"),
                "checkbox_indicator_checked_bg": QColor("#4682B4"),
                "checkbox_indicator_border": QColor("#0077CC"),
                "line_edit_bg": QColor("#004080"),
                "line_edit_text": QColor("#E0FFFF"),
                "line_edit_border": QColor("#005099"),
                "button_bg": QColor("#4682B4"),
                "button_hover_bg": QColor("#3A719D"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#004488"),
                "scrollbar_handle": QColor("#4682B4"),
                "scrollbar_button": QColor("#4682B4"),
            },
            "vibrant_purple_theme": {
                "normal_text": QColor("#E6E6FA"), # Lavender
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#7FFF00"), # Chartreuse
                "group_box_border": QColor("#8A2BE2"),
                "group_box_bg": QColor("rgba(75, 0, 130, 0.7)"),
                "group_box_title": QColor("#DDA0DD"),
                "checkbox_color": QColor("#E6E6FA"),
                "checkbox_indicator_unchecked_bg": QColor("#5F2A80"),
                "checkbox_indicator_checked_bg": QColor("#8A2BE2"),
                "checkbox_indicator_border": QColor("#B266FF"),
                "line_edit_bg": QColor("#5F2A80"),
                "line_edit_text": QColor("#E6E6FA"),
                "line_edit_border": QColor("#8A2BE2"),
                "button_bg": QColor("#8A2BE2"),
                "button_hover_bg": QColor("#7B1BE0"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#6A0DAD"),
                "scrollbar_handle": QColor("#8A2BE2"),
                "scrollbar_button": QColor("#8A2BE2"),
            },
            "light_modern_theme": {
                "normal_text": QColor("#333333"),
                "warning_text": QColor("#FF4500"),
                "success_text": QColor("#28A745"),
                "group_box_border": QColor("#A0A0A0"),
                "group_box_bg": QColor("rgba(248, 248, 248, 0.9)"),
                "group_box_title": QColor("#555555"),
                "checkbox_color": QColor("#333333"),
                "checkbox_indicator_unchecked_bg": QColor("#CCCCCC"),
                "checkbox_indicator_checked_bg": QColor("#607D8B"),
                "checkbox_indicator_border": QColor("#999999"),
                "line_edit_bg": QColor("#FFFFFF"),
                "line_edit_text": QColor("#333333"),
                "line_edit_border": QColor("#C0C0C0"),
                "button_bg": QColor("#607D8B"),
                "button_hover_bg": QColor("#455A64"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#E8E8E8"),
                "scrollbar_handle": QColor("#607D8B"),
                "scrollbar_button": QColor("#607D8B"),
            },
            "high_contrast_theme": {
                "normal_text": QColor("#FFFF00"), # Yellow
                "warning_text": QColor("#FF0000"), # Red
                "success_text": QColor("#00FF00"), # Green
                "group_box_border": QColor("#00FFFF"), # Cyan
                "group_box_bg": QColor("rgba(0, 0, 0, 0.9)"),
                "group_box_title": QColor("#FF0000"),
                "checkbox_color": QColor("#FFFF00"),
                "checkbox_indicator_unchecked_bg": QColor("#555555"),
                "checkbox_indicator_checked_bg": QColor("#FFFF00"),
                "checkbox_indicator_border": QColor("#00FFFF"),
                "line_edit_bg": QColor("#222222"),
                "line_edit_text": QColor("#FFFF00"),
                "line_edit_border": QColor("#FF00FF"),
                "button_bg": QColor("#FF00FF"),
                "button_hover_bg": QColor("#CC00CC"),
                "button_text": QColor("white"),
                "scrollbar_trough": QColor("#333333"),
                "scrollbar_handle": QColor("#FFFF00"),
                "scrollbar_button": QColor("#FF00FF"),
            }
        }

        self.theme_palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"]) # Fallback to dark
        
        self.normal_text_color = self.theme_palette["normal_text"]
        self.warning_text_color = self.theme_palette["warning_text"]
        self.success_text_color = self.theme_palette["success_text"]
        self.group_box_border_color = self.theme_palette["group_box_border"]
        self.group_box_bg_color = self.theme_palette["group_box_bg"]
        self.group_box_title_color = self.theme_palette["group_box_title"]
        self.checkbox_color = self.theme_palette["checkbox_color"]
        self.checkbox_indicator_unchecked_bg_color = self.theme_palette["checkbox_indicator_unchecked_bg"]
        self.checkbox_indicator_checked_bg_color = self.theme_palette["checkbox_indicator_checked_bg"]
        self.checkbox_indicator_border_color = self.theme_palette["checkbox_indicator_border"]
        self.line_edit_bg_color = self.theme_palette["line_edit_bg"]
        self.line_edit_text_color = self.theme_palette["line_edit_text"]
        self.line_edit_border_color = self.theme_palette["line_edit_border"]
        self.button_bg_color = self.theme_palette["button_bg"]
        self.button_hover_bg_color = self.theme_palette["button_hover_bg"]
        self.button_text_color = self.theme_palette["button_text"]
        self.scrollbar_trough_color = self.theme_palette["scrollbar_trough"]
        self.scrollbar_handle_color = self.theme_palette["scrollbar_handle"]
        self.scrollbar_button_color = self.theme_palette["scrollbar_button"]

        # Update dynamic elements
        # Using a guard clause here to prevent errors if widgets are not yet initialized
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
        
        if hasattr(self, 'log_dir_space_label'):
            # These are updated in _update_storage_status_display, but ensure initial color is set
            self.log_dir_space_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
            self.archive_dir_space_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
            self.sensor_log_space_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
                
        # Re-apply stylesheet to ensure all QSS rules with dynamic colors are updated
        self.set_style()


    def _setup_ui(self):
        """Sets up the UI elements for the settings tab."""
        # Use objectName for the title label for consistent styling
        self.title_label = QLabel("Application Settings")
        self.title_label.setObjectName("settingsTabTitleLabel")
        self.title_label.setFont(QFont("Inter", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignLeft) # Changed alignment to left
        self.title_label.setContentsMargins(0, 20, 0, 20)
        self.main_layout.addWidget(self.title_label)

        scroll_area = QScrollArea(self)
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("settingsScrollArea")
        
        content_widget = QWidget()
        content_widget.setObjectName("settingsContentWidget")
        # Explicitly set the size policy for the content widget
        content_widget.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding) 
        scroll_area.setWidget(content_widget)
        
        content_layout = QVBoxLayout(content_widget)
        content_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        # Sensor Mode Settings Group
        sensor_mode_group = QGroupBox("Sensor Mode")
        sensor_mode_group.setObjectName("settingsGroupBox")
        sensor_mode_group.setFont(QFont("Inter", 14, QFont.Bold))
        sensor_mode_layout = QFormLayout(sensor_mode_group)

        self.mock_sensors_checkbox = QCheckBox("Enable Mock Sensors (Requires App Restart)")
        self.mock_sensors_checkbox.setObjectName("settingsCheckBox")
        self.mock_sensors_checkbox.setChecked(self.config.get_setting("enable_mock_sensors", True))
        self.mock_sensors_checkbox.stateChanged.connect(self._save_sensor_mode_setting)
        sensor_mode_layout.addRow(self.mock_sensors_checkbox)
        
        content_layout.addWidget(sensor_mode_group)
        content_layout.addSpacing(20)


        # Logging Settings Group
        logging_group = QGroupBox("Logging Settings")
        logging_group.setObjectName("settingsGroupBox")
        logging_group.setFont(QFont("Inter", 14, QFont.Bold))
        logging_layout = QFormLayout(logging_group)

        self.debug_console_checkbox = QCheckBox("Enable Debug messages to console")
        self.debug_console_checkbox.setObjectName("settingsCheckBox")
        self.debug_console_checkbox.setChecked(self.config.get_setting("enable_debug_to_console", True))
        self.debug_console_checkbox.stateChanged.connect(self._save_logging_settings)
        logging_layout.addRow(self.debug_console_checkbox)

        self.debug_file_checkbox = QCheckBox("Enable Debug messages to file")
        self.debug_file_checkbox.setObjectName("settingsCheckBox")
        self.debug_file_checkbox.setChecked(self.config.get_setting("enable_debug_to_file", True))
        self.debug_file_checkbox.stateChanged.connect(self._save_logging_settings)
        logging_layout.addRow(self.debug_file_checkbox)

        self.log_dir_edit = QLineEdit(self.config.get_setting("log_directory", "Debug_Logs"))
        self.log_dir_edit.setObjectName("settingsLineEdit")
        self.log_dir_button = QPushButton("Browse")
        self.log_dir_button.setObjectName("settingsButton")
        self.log_dir_button.clicked.connect(lambda: self._browse_directory(self.log_dir_edit, "log_directory", is_logging_dir=True))
        log_dir_layout = QHBoxLayout()
        log_dir_layout.addWidget(self.log_dir_edit)
        log_dir_layout.addWidget(self.log_dir_button)
        logging_layout.addRow("Debug Log Directory:", log_dir_layout)

        self.sensor_log_checkbox = QCheckBox("Enable Sensor value logging to CSV")
        self.sensor_log_checkbox.setObjectName("settingsCheckBox")
        self.sensor_log_checkbox.setChecked(self.config.get_setting("enable_sensor_logging", True))
        self.sensor_log_checkbox.stateChanged.connect(self._save_logging_settings)
        logging_layout.addRow(self.sensor_log_checkbox)

        self.sensor_log_dir_edit = QLineEdit(self.config.get_setting("sensor_log_directory", "Sensor_Logs"))
        self.sensor_log_dir_edit.setObjectName("settingsLineEdit")
        self.sensor_log_dir_button = QPushButton("Browse")
        self.sensor_log_dir_button.setObjectName("settingsButton")
        self.sensor_log_dir_button.clicked.connect(lambda: self._browse_directory(self.sensor_log_dir_edit, "sensor_log_directory", is_logging_dir=True))
        sensor_log_dir_layout = QHBoxLayout()
        sensor_log_dir_layout.addWidget(self.sensor_log_dir_edit)
        sensor_log_dir_layout.addWidget(self.sensor_log_dir_button)
        logging_layout.addRow("Sensor Log Directory:", sensor_log_dir_layout)
        
        content_layout.addWidget(logging_group)
        content_layout.addSpacing(20)

        # Archiving Settings Group
        archive_group = QGroupBox("Archive Settings")
        archive_group.setObjectName("settingsGroupBox")
        archive_group.setFont(QFont("Inter", 14, QFont.Bold))
        archive_layout = QFormLayout(archive_group)

        self.enable_archive_checkbox = QCheckBox("Enable Archive (logs, etc.)")
        self.enable_archive_checkbox.setObjectName("settingsCheckBox")
        self.enable_archive_checkbox.setChecked(self.config.get_setting("enable_archive", True))
        self.enable_archive_checkbox.stateChanged.connect(self._save_archive_settings)
        archive_layout.addRow(self.enable_archive_checkbox)

        self.archive_dir_edit = QLineEdit(self.config.get_setting("archive_directory", "Archive_Sensor_Logs"))
        self.archive_dir_edit.setObjectName("settingsLineEdit")
        self.archive_dir_button = QPushButton("Browse")
        self.archive_dir_button.setObjectName("settingsButton")
        self.archive_dir_button.clicked.connect(lambda: self._browse_directory(self.archive_dir_edit, "archive_directory"))
        archive_dir_layout = QHBoxLayout()
        archive_dir_layout.addWidget(self.archive_dir_edit)
        archive_dir_layout.addWidget(self.archive_dir_button)
        archive_layout.addRow("Archive Directory:", archive_dir_layout)
        
        content_layout.addWidget(archive_group)
        content_layout.addSpacing(20)

        # Weather Settings Group
        weather_group = QGroupBox("Weather API Settings")
        weather_group.setObjectName("settingsGroupBox")
        weather_group.setFont(QFont("Inter", 14, QFont.Bold))
        weather_layout = QFormLayout(weather_group)

        self.api_key_edit = QLineEdit(self.config.get_setting("openweathermap_api_key", ""))
        self.api_key_edit.setObjectName("settingsLineEdit")
        self.api_key_edit.setPlaceholderText("Enter OpenWeatherMap API Key")
        self.api_key_edit.editingFinished.connect(self._save_weather_settings) # Save when editing finishes
        weather_layout.addRow("OpenWeatherMap API Key:", self.api_key_edit)

        self.city_edit = QLineEdit(self.config.get_setting("weather_city", "Frisco"))
        self.city_edit.setObjectName("settingsLineEdit")
        self.city_edit.editingFinished.connect(self._save_weather_settings)
        weather_layout.addRow("City:", self.city_edit)

        self.country_code_edit = QLineEdit(self.config.get_setting("weather_country_code", "US"))
        self.country_code_edit.setObjectName("settingsLineEdit")
        self.country_code_edit.setPlaceholderText("e.g., US, GB, DE")
        self.country_code_edit.editingFinished.connect(self._save_weather_settings)
        weather_layout.addRow("Country Code:", self.country_code_edit)
        
        content_layout.addWidget(weather_group)
        content_layout.addSpacing(20)

        # Sensor Interval Settings
        sensor_interval_group = QGroupBox("Sensor Read Interval")
        sensor_interval_group.setObjectName("settingsGroupBox")
        sensor_interval_group.setFont(QFont("Inter", 14, QFont.Bold))
        sensor_interval_layout = QFormLayout(sensor_interval_group)

        self.sensor_interval_edit = QLineEdit(str(self.config.get_setting("sensor_read_interval", 2)))
        self.sensor_interval_edit.setObjectName("settingsLineEdit")
        self.sensor_interval_edit.setToolTip("Interval in seconds for reading sensors.")
        self.sensor_interval_edit.editingFinished.connect(self._save_sensor_interval)
        sensor_interval_layout.addRow("Read Interval (seconds):", self.sensor_interval_edit)

        content_layout.addWidget(sensor_interval_group)
        content_layout.addSpacing(20)

        # Storage Status
        storage_status_group = QGroupBox("Storage Status")
        storage_status_group.setObjectName("settingsGroupBox")
        storage_status_group.setFont(QFont("Inter", 14, QFont.Bold))
        storage_status_layout = QVBoxLayout(storage_status_group)
        
        self.log_dir_space_label = QLabel("Debug Log Dir: Calculating...")
        self.log_dir_space_label.setObjectName("settingsLabel") # Add object name
        self.archive_dir_space_label = QLabel("Archive Dir: Calculating...")
        self.archive_dir_space_label.setObjectName("settingsLabel") # Add object name
        self.sensor_log_space_label = QLabel("Sensor Log Dir: Calculating...") # Added label for sensor log
        self.sensor_log_space_label.setObjectName("settingsLabel") # Add object name
        
        storage_status_layout.addWidget(self.log_dir_space_label)
        storage_status_layout.addWidget(self.archive_dir_space_label)
        storage_status_layout.addWidget(self.sensor_log_space_label) # Add to layout
        
        refresh_storage_button = QPushButton("Refresh Storage Status")
        refresh_storage_button.setObjectName("settingsButton")
        refresh_storage_button.clicked.connect(self._update_storage_status_display)
        storage_status_layout.addWidget(refresh_storage_button, alignment=Qt.AlignCenter)

        content_layout.addWidget(storage_status_group)

        # Add a stretch at the end of the content_layout to push everything to the top
        content_layout.addStretch(1) 

        self.main_layout.addWidget(scroll_area)
        # Removed the redundant stretch from main_layout: self.main_layout.addStretch(1) 

        self._update_storage_status_display() # Initial display of storage status
        
        # --- Debugging Statements ---
        self.logger.debug("SettingsTab size: {}".format(self.size()))
        self.logger.debug("ScrollArea sizeHint: {}".format(scroll_area.sizeHint()))
        self.logger.debug("ContentWidget sizeHint: {}".format(content_widget.sizeHint()))
        self.logger.debug("ContentLayout minimumSize: {}".format(content_layout.minimumSize()))
        self.logger.debug("ContentLayout sizeHint: {}".format(content_layout.sizeHint()))
        # --- End Debugging Statements ---


    def _browse_directory(self, line_edit, config_key, is_logging_dir=False):
        """Opens a directory dialog and updates the line edit and config."""
        current_dir = line_edit.text()
        # To make sure it always points to a valid starting directory
        # We need to resolve it relative to the project root first, then check if it exists
        project_root_abs = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))
        resolved_path = os.path.join(project_root_abs, current_dir)
        
        if not os.path.exists(resolved_path):
            current_dir = os.path.expanduser("~") # Default to home if current path is invalid
        else:
            current_dir = resolved_path

        directory = QFileDialog.getExistingDirectory(self, "Select Directory", current_dir)
        if directory:
            # Get path relative to project root if possible, otherwise use absolute path
            relative_path = os.path.relpath(directory, project_root_abs)
            
            # A common way to check if a path is a subpath of another is to see if relpath doesn't start with '..'
            if not relative_path.startswith('..') and not os.path.isabs(relative_path): 
                line_edit.setText(relative_path)
            else: # Otherwise, save absolute path
                line_edit.setText(directory)
            
            self.config.set_setting(config_key, line_edit.text())
            
            # Re-initialize logger if log directories change
            if is_logging_dir:
                # To prevent duplicate handlers, we manually clear and re-add handlers
                logger_instance = Logger.get_logger()
                for handler in logger_instance.handlers[:]: # Iterate over a copy
                    logger_instance.removeHandler(handler)
                    handler.close() # Close the handler to release file resources
                
                Logger.initialize(
                    debug_to_console=self.config.get_setting("enable_debug_to_console", True),
                    debug_to_file=self.config.get_setting("enable_debug_to_file", True),
                    log_dir=self.config.get_setting("log_directory", "Debug_Logs") # Use potentially updated log directory
                )
                self.sensor_manager._setup_logging_files() # Re-create sensor log file if path changed
            self.logger.info("Updated directory for {}: {}".format(config_key, line_edit.text()))
            self._update_storage_status_display() # Update storage status after path change
            self.settings_updated.emit() # Emit signal after successful directory change

    def _save_sensor_mode_setting(self):
        """Saves the mock sensor setting and prompts for restart."""
        self.config.set_setting("enable_mock_sensors", self.mock_sensors_checkbox.isChecked())
        QMessageBox.information(self, "Setting Changed", 
                                "Sensor mode changed. Please restart the application for the change to take effect.")
        self.logger.info("Mock sensor mode set to: {}".format(self.mock_sensors_checkbox.isChecked()))
        self.settings_updated.emit() # Emit signal

    def _save_logging_settings(self):
        """Saves logging-related checkbox settings and re-initializes logger."""
        self.config.set_setting("enable_debug_to_console", self.debug_console_checkbox.isChecked())
        self.config.set_setting("enable_debug_to_file", self.debug_file_checkbox.isChecked())
        self.config.set_setting("enable_sensor_logging", self.sensor_log_checkbox.isChecked())
        
        # Re-initialize logger to apply new debug settings immediately
        logger_instance = Logger.get_logger()
        for handler in logger_instance.handlers[:]: # Clear existing handlers
            logger_instance.removeHandler(handler)
            handler.close()
            
        Logger.initialize(
            debug_to_console=self.debug_console_checkbox.isChecked(),
            debug_to_file=self.debug_file_checkbox.isChecked(),
            log_dir=self.config.get_setting("log_directory", "Debug_Logs") # Use potentially updated log directory
        )
        self.sensor_manager._setup_logging_files() # Ensure sensor logging path is updated
        self.logger.info("Logging settings saved.")
        self.settings_updated.emit() # Emit signal

    def _save_archive_settings(self):
        """Saves archive-related checkbox settings."""
        self.config.set_setting("enable_archive", self.enable_archive_checkbox.isChecked())
        self.logger.info("Archive settings saved.")
        self.settings_updated.emit() # Emit signal

    def _save_weather_settings(self):
        """Saves weather API and location settings."""
        self.config.set_setting("openweathermap_api_key", self.api_key_edit.text().strip())
        self.config.set_setting("weather_city", self.city_edit.text().strip())
        self.config.set_setting("weather_country_code", self.country_code_edit.text().strip())
        self.logger.info("Weather settings saved.")
        self.settings_updated.emit() # Emit signal

    def _save_sensor_interval(self):
        """Saves the sensor read interval, validating input."""
        try:
            interval_str = self.sensor_interval_edit.text().strip()
            interval = int(interval_str)
            if interval <= 0:
                raise ValueError("Interval must be a positive integer.")
            self.config.set_setting("sensor_read_interval", interval)
            self.logger.info("Sensor read interval updated to {} seconds.".format(interval))
            # Inform user that thread restart is needed for immediate effect
            QMessageBox.information(self, "Setting Saved", "Sensor read interval updated. Please restart the application for the change to take full effect on the sensor reading thread.")
            self.settings_updated.emit() # Emit signal
        except ValueError as e:
            QMessageBox.warning(self, "Invalid Input", "Please enter a valid positive integer for sensor read interval. ({})".format(e))
            self.sensor_interval_edit.setText(str(self.config.get_setting("sensor_read_interval", 2))) # Revert to last valid
        except Exception as e:
            self.logger.error("Error saving sensor interval: {}".format(e))
            QMessageBox.critical(self, "Error", "Failed to save sensor interval: {}".format(e))

    def _update_storage_status_display(self):
        """Updates the labels displaying free storage space."""
        # This method is called both on initial setup and when refreshing storage.
        # Ensure theme colors are re-applied to handle potential theme changes while app is running.
        self._set_theme_colors() 

        # Resolve to absolute paths for storage check, then check
        project_root_abs = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir))

        log_dir = self.config.get_setting("log_directory", "Debug_Logs")
        archive_dir = self.config.get_setting("archive_directory", "Archive_Sensor_Logs")
        sensor_log_dir = self.config.get_setting("sensor_log_directory", "Sensor_Logs")

        # Construct absolute paths
        log_abs_path = os.path.join(project_root_abs, log_dir)
        archive_abs_path = os.path.join(project_root_abs, archive_dir)
        sensor_log_abs_path = os.path.join(project_root_abs, sensor_log_dir)

        # Ensure directories exist before checking space
        for path in [log_abs_path, archive_abs_path, sensor_log_abs_path]:
            if not os.path.exists(path):
                try:
                    os.makedirs(path)
                except Exception as e:
                    self.logger.error("Failed to create directory {}: {}".format(path, e))

        log_free_gb = self.storage_monitor.get_free_space_gb(log_abs_path)
        archive_free_gb = self.storage_monitor.get_free_space_gb(archive_abs_path)
        sensor_log_free_gb = self.storage_monitor.get_free_space_gb(sensor_log_abs_path)

        self.log_dir_space_label.setText("Debug Log Dir ({}): {:.2f} GB free".format(os.path.basename(log_abs_path), log_free_gb))
        self.archive_dir_space_label.setText("Archive Dir ({}): {:.2f} GB free".format(os.path.basename(archive_abs_path), archive_free_gb))
        self.sensor_log_space_label.setText("Sensor Log Dir ({}): {:.2f} GB free".format(os.path.basename(sensor_log_abs_path), sensor_log_free_gb))

        # Apply color warnings based on theme colors
        min_space = self.config.get_setting("min_free_space_gb", 0.5)
        
        if log_free_gb < min_space: self.log_dir_space_label.setStyleSheet("color: {};".format(self.warning_text_color.name()))
        else: self.log_dir_space_label.setStyleSheet("color: {};".format(self.success_text_color.name()))

        if archive_free_gb < min_space: self.archive_dir_space_label.setStyleSheet("color: {};".format(self.warning_text_color.name()))
        else: self.archive_dir_space_label.setStyleSheet("color: {};".format(self.success_text_color.name()))
        
        if sensor_log_free_gb < min_space: self.sensor_log_space_label.setStyleSheet("color: {};".format(self.warning_text_color.name()))
        else: self.sensor_log_space_label.setStyleSheet("color: {};".format(self.success_text_color.name()))

    def set_style(self):
        """Applies specific styling for the tab."""
        self.setStyleSheet("""
            QWidget#SettingsTab {{
                background-color: transparent;
            }}
            QLabel#settingsTabTitleLabel {{
                color: {normal_text_color};
            }}
            QLabel#settingsLabel {{ /* General QLabel style within this tab, applied via objectName */
                color: {normal_text_color};
            }}
            QLabel#settingsLabel:hover {{
                color: {normal_text_color}; /* Keep same or define a hover color */
            }}
            /* Apply normal_text_color to all QLabels that are direct children of QGroupBoxes */
            QGroupBox QLabel {{
                color: {normal_text_color};
            }}
            QGroupBox#settingsGroupBox {{
                border: 1px solid {group_box_border_color};
                border-radius: 10px;
                margin-top: 10px;
                background-color: {group_box_bg_color};
                padding: 20px 10px 10px 10px; /* Increased top padding to make space for title */
            }}
            QGroupBox::title {{
                subcontrol-origin: padding; /* Origin from padding area */
                subcontrol-position: top left; /* Position at top left */
                margin-top: -10px; /* Pull the title up to overlap the border */
                padding: 0 5px; /* Adjust padding around title text */
                color: {group_box_title_color};
            }}
            QCheckBox#settingsCheckBox {{
                color: {checkbox_color}; /* Dynamic color for checkboxes text */
            }}
            QCheckBox::indicator {{
                width: 18px;
                height: 18px;
                border: 1px solid {checkbox_indicator_border_color}; /* Dynamic border color */
                border-radius: 3px; /* Slightly rounded corners for indicator */
            }}
            QCheckBox::indicator:unchecked {{
                background-color: {checkbox_indicator_unchecked_bg_color}; /* Dynamic unchecked background */
            }}
            QCheckBox::indicator:checked {{
                background-color: {checkbox_indicator_checked_bg_color}; /* Dynamic checked background */
                image: url(icons/checkbox_checked_tick.png); /* You might need to provide a tick icon */
                /* A simple white/theme-appropriate checkmark can be drawn using image property or by a separate font icon */
            }}
            QLineEdit#settingsLineEdit {{
                background-color: {line_edit_bg_color};
                color: {line_edit_text_color};
                border: 1px solid {line_edit_border_color};
                border-radius: 5px;
                padding: 5px;
            }}
            QPushButton#settingsButton {{
                background-color: {button_bg_color};
                color: {button_text_color};
                border-radius: 5px;
                padding: 5px 10px;
            }}
            QPushButton#settingsButton:hover {{
                background-color: {button_hover_bg_color};
            }}
            QScrollArea#settingsScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QWidget#settingsContentWidget {{ /* Targets the content widget inside the scroll area */
                background-color: transparent;
            }}
            /* Scrollbar styling */
            QScrollBar:vertical {{
                border: 1px solid {scrollbar_trough_color};
                background: {scrollbar_trough_color};
                width: 10px;
                margin: 20px 0 20px 0; /* Space for buttons */
                border-radius: 5px;
            }}
            QScrollBar::handle:vertical {{
                background: {scrollbar_handle_color};
                min-height: 20px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: 1px solid {scrollbar_button_color};
                background: {scrollbar_button_color};
                height: 20px;
                subcontrol-origin: margin;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical {{
                subcontrol-position: bottom;
            }}
            QScrollBar::sub-line:vertical {{
                subcontrol-position: top;
            }}
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
                background: none;
            }}
        """.format(
            normal_text_color=self.normal_text_color.name(),
            group_box_border_color=self.group_box_border_color.name(),
            group_box_bg_color=self.group_box_bg_color.name(),
            group_box_title_color=self.group_box_title_color.name(),
            checkbox_color=self.checkbox_color.name(),
            checkbox_indicator_unchecked_bg_color=self.checkbox_indicator_unchecked_bg_color.name(),
            checkbox_indicator_checked_bg_color=self.checkbox_indicator_checked_bg_color.name(),
            checkbox_indicator_border_color=self.checkbox_indicator_border_color.name(),
            line_edit_bg_color=self.line_edit_bg_color.name(),
            line_edit_text_color=self.line_edit_text_color.name(),
            line_edit_border_color=self.line_edit_border_color.name(),
            button_bg_color=self.button_bg_color.name(),
            button_hover_bg_color=self.button_hover_bg_color.name(),
            button_text_color=self.button_text_color.name(),
            scrollbar_trough_color=self.scrollbar_trough_color.name(),
            scrollbar_handle_color=self.scrollbar_handle_color.name(),
            scrollbar_button_color=self.scrollbar_button_color.name()
        ))
