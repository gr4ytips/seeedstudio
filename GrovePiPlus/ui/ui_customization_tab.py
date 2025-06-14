# ui/ui_customization_tab.py
import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QPushButton, QHBoxLayout, QFrame
from PyQt5.QtCore import Qt, pyqtSignal # Import pyqtSignal
from PyQt5.QtGui import QFont, QColor # Import QColor for theme palette

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.logger import Logger
from utils.config_manager import ConfigManager

class UICustomizationTab(QWidget):
    """
    Separate tab for UI customization, specifically theme selection and sensor display type.
    """
    theme_changed = pyqtSignal(str) # Define a signal that emits a string (theme name)
    sensor_display_type_changed = pyqtSignal(str) # New signal for sensor display type

    def __init__(self, main_window_ref, parent=None):
        super(UICustomizationTab, self).__init__(parent)
        self.logger = Logger.get_logger()
        self.config = ConfigManager.get_instance()
        self.main_window_ref = main_window_ref # Reference to the main window to call apply_theme

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        
        self._set_theme_colors() # Set initial theme colors
        self._setup_ui()
        self.set_style()
        self.logger.info("UICustomizationTab initialized.")

    def _set_theme_colors(self):
        """Sets internal color attributes based on the current theme for dynamic elements."""
        current_theme = self.config.get_setting("current_theme", "dark_theme")

        theme_palettes = {
            "dark_theme": {
                "label_color": QColor("#abb2bf"),
                "combo_bg": QColor("#3e4451"),
                "combo_text": QColor("#abb2bf"),
                "combo_border": QColor("#5c6370"),
                "button_bg": QColor("#61afef"),
                "button_text": QColor("#ffffff"),
                "frame_bg": QColor("rgba(40, 40, 40, 0.7)"),
                "frame_border": QColor("#666"),
            },
            "light_theme": {
                "label_color": QColor("#333333"),
                "combo_bg": QColor("#f8f8f8"),
                "combo_text": QColor("#333333"),
                "combo_border": QColor("#ccc"),
                "button_bg": QColor("#007bff"),
                "button_text": QColor("#ffffff"),
                "frame_bg": QColor("rgba(255, 255, 255, 0.7)"),
                "frame_border": QColor("#ccc"),
            },
            "blue_theme": {
                "label_color": QColor("#e0f2f7"),
                "combo_bg": QColor("#223f5b"),
                "combo_text": QColor("#e0f2f7"),
                "combo_border": QColor("#4a6c8e"),
                "button_bg": QColor("#4682B4"),
                "button_text": QColor("#ffffff"),
                "frame_bg": QColor("rgba(26, 42, 64, 0.7)"),
                "frame_border": QColor("#3c6595"),
            },
            "dark_gray_theme": {
                "label_color": QColor("#fdfdfd"),
                "combo_bg": QColor("#4b4f52"),
                "combo_text": QColor("#fdfdfd"),
                "combo_border": QColor("#6c7072"),
                "button_bg": QColor("#6a737d"),
                "button_text": QColor("#ffffff"),
                "frame_bg": QColor("rgba(60, 63, 65, 0.7)"),
                "frame_border": QColor("#666"),
            },
            "forest_green_theme": {
                "label_color": QColor("#FFFFFF"),
                "combo_bg": QColor("#339933"),
                "combo_text": QColor("#FFFFFF"),
                "combo_border": QColor("#4CAF50"),
                "button_bg": QColor("#66BB6A"),
                "button_text": QColor("#FFFFFF"),
                "frame_bg": QColor("rgba(34, 139, 34, 0.7)"),
                "frame_border": QColor("#66BB6A"),
            },
            "warm_sepia_theme": {
                "label_color": QColor("#F5DEB3"),
                "combo_bg": QColor("#7C4F2A"),
                "combo_text": QColor("#F5DEB3"),
                "combo_border": QColor("#A0522D"),
                "button_bg": QColor("#A0522D"),
                "button_text": QColor("#FFFFFF"),
                "frame_bg": QColor("rgba(112, 66, 20, 0.7)"),
                "frame_border": QColor("#A0522D"),
            },
            "ocean_blue_theme": {
                "label_color": QColor("#E0FFFF"),
                "combo_bg": QColor("#004080"),
                "combo_text": QColor("#E0FFFF"),
                "combo_border": QColor("#005099"),
                "button_bg": QColor("#4682B4"),
                "button_text": QColor("#FFFFFF"),
                "frame_bg": QColor("rgba(0, 51, 102, 0.7)"),
                "frame_border": QColor("#0066CC"),
            },
            "vibrant_purple_theme": {
                "label_color": QColor("#E6E6FA"),
                "combo_bg": QColor("#5F2A80"),
                "combo_text": QColor("#E6E6FA"),
                "combo_border": QColor("#8A2BE2"),
                "button_bg": QColor("#8A2BE2"),
                "button_text": QColor("#FFFFFF"),
                "frame_bg": QColor("rgba(75, 0, 130, 0.7)"),
                "frame_border": QColor("#8A2BE2"),
            },
            "light_modern_theme": {
                "label_color": QColor("#333333"),
                "combo_bg": QColor("#FFFFFF"),
                "combo_text": QColor("#333333"),
                "combo_border": QColor("#C0C0C0"),
                "button_bg": QColor("#607D8B"),
                "button_text": QColor("#FFFFFF"),
                "frame_bg": QColor("rgba(224, 224, 224, 0.7)"),
                "frame_border": QColor("#A0A0A0"),
            },
            "high_contrast_theme": {
                "label_color": QColor("#FFFF00"),
                "combo_bg": QColor("#222222"),
                "combo_text": QColor("#FFFF00"),
                "combo_border": QColor("#FF00FF"),
                "button_bg": QColor("#FF00FF"),
                "button_text": QColor("#000000"),
                "frame_bg": QColor("rgba(0, 0, 0, 0.7)"),
                "frame_border": QColor("#FF00FF"),
            }
        }

        self.theme_palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"])

    def _setup_ui(self):
        """Sets up the UI elements for the UI customization tab."""
        # Use objectName for the title label for consistent styling
        self.title_label = QLabel("UI Customization") # Changed title
        self.title_label.setObjectName("uiCustomizationTabTitleLabel")
        self.title_label.setFont(QFont("Inter", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setContentsMargins(0, 20, 0, 20)
        self.main_layout.addWidget(self.title_label)

        # Use objectName for content frame for consistent styling
        self.content_frame = QFrame(self)
        self.content_frame.setFrameShape(QFrame.StyledPanel)
        self.content_frame.setFrameShadow(QFrame.Raised)
        self.content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setAlignment(Qt.AlignCenter)

        # Theme Selection Group
        theme_group_layout = QVBoxLayout()
        self.theme_label = QLabel("Select Theme:")
        self.theme_label.setObjectName("themeLabel")
        self.theme_label.setFont(QFont("Inter", 16))
        theme_group_layout.addWidget(self.theme_label, alignment=Qt.AlignCenter)

        self.theme_combo = QComboBox()
        self.theme_combo.setFont(QFont("Inter", 12))
        self.theme_combo.setFixedSize(250, 40)
        self._populate_themes()
        theme_group_layout.addWidget(self.theme_combo, alignment=Qt.AlignCenter)

        self.apply_button = QPushButton("Apply Theme")
        self.apply_button.setFont(QFont("Inter", 14, QFont.Bold))
        self.apply_button.setFixedSize(180, 50)
        self.apply_button.clicked.connect(self._apply_selected_theme)
        theme_group_layout.addWidget(self.apply_button, alignment=Qt.AlignCenter)
        content_layout.addLayout(theme_group_layout)

        # Add some spacing between theme and sensor type selection
        content_layout.addSpacing(30)

        # Sensor Display Type Selection Group (NEW)
        sensor_type_group_layout = QVBoxLayout()
        self.sensor_type_label = QLabel("Select Sensor Display Type:")
        self.sensor_type_label.setObjectName("themeLabel") # Reusing themeLabel style
        self.sensor_type_label.setFont(QFont("Inter", 16))
        sensor_type_group_layout.addWidget(self.sensor_type_label, alignment=Qt.AlignCenter)

        self.sensor_type_combo = QComboBox()
        self.sensor_type_combo.setFont(QFont("Inter", 12))
        self.sensor_type_combo.setFixedSize(250, 40)
        self.sensor_type_options = ["Default Gauge", "Gauge Widget Multi Ring", "Gauge Widget One"]
        self.sensor_type_combo.addItems(self.sensor_type_options)
        
        # Set initial selection from config
        current_sensor_type = self.config.get_setting("sensor_display_type", "Default Gauge")
        idx = self.sensor_type_combo.findText(current_sensor_type)
        if idx != -1:
            self.sensor_type_combo.setCurrentIndex(idx)
        else:
            self.sensor_type_combo.setCurrentIndex(0) # Fallback to default
            self.config.set_setting("sensor_display_type", "Default Gauge") # Save default if not found

        self.sensor_type_combo.currentIndexChanged.connect(self._apply_selected_sensor_display_type)
        sensor_type_group_layout.addWidget(self.sensor_type_combo, alignment=Qt.AlignCenter)
        content_layout.addLayout(sensor_type_group_layout)


        content_layout.addStretch(1) # Push content to top
        self.main_layout.addWidget(self.content_frame, alignment=Qt.AlignCenter)
        self.main_layout.addStretch(1)

    def _populate_themes(self):
        """Discovers available QSS theme files and populates the combo box."""
        theme_dir = os.path.join(project_root, 'themes')
        if not os.path.exists(theme_dir):
            os.makedirs(theme_dir) # Create if doesn't exist
            self.logger.warning("Themes directory not found, created: {}".format(theme_dir))

        themes = []
        # Define all expected themes here to ensure they are always listed
        # regardless of whether their QSS files exist yet.
        # This makes it easier for the user to select them and then
        # allows _create_default_theme_files to create missing ones.
        all_expected_themes = [
            "dark_theme",
            "light_theme",
            "blue_theme",
            "dark_gray_theme",
            "forest_green_theme",
            "warm_sepia_theme",
            "ocean_blue_theme",
            "vibrant_purple_theme",
            "light_modern_theme",
            "high_contrast_theme"
        ]
        
        # Populate the combo box with all expected themes
        self.theme_combo.addItems(all_expected_themes)

        # Create missing default theme files
        self._create_default_theme_files()

        # Try to set the current theme from config
        current_theme = self.config.get_setting("current_theme", "dark_theme")
        idx = self.theme_combo.findText(current_theme)
        if idx != -1:
            self.theme_combo.setCurrentIndex(idx)
        else:
            self.logger.warning("Current theme '{}' not found in available themes. Setting to first available.".format(current_theme))
            if all_expected_themes:
                self.theme_combo.setCurrentIndex(0)
                self.config.set_setting("current_theme", all_expected_themes[0])


    def _create_default_theme_files(self):
        """Creates basic default theme QSS files if they are missing."""
        theme_dir = os.path.join(project_root, 'themes')
        
        dark_theme_content = """
            QMainWindow {
                background-color: #282c34; /* Dark background */
                color: #abb2bf; /* Light gray text */
            }
            QTabWidget::pane {
                border: 1px solid #444;
                background: #21252b;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #3a3f4b;
                color: #abb2bf;
                border: 1px solid #444;
                border-bottom-color: #3a3f4b;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #31353c;
                border-color: #444;
                border-bottom-color: #31353c;
            }
            QTabBar::tab:hover {
                background: #4a505b;
            }
            QLabel {
                color: #abb2bf;
            }
            QGroupBox {
                border: 1px solid #555;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #282c34;
            }
            QGroupBox::title {
                color: #61afef; /* Blue */
            }
            QPushButton {
                background-color: #61afef; /* Blue */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #52a0e0;
            }
            QLineEdit {
                background-color: #3e4451;
                color: #abb2bf;
                border: 1px solid #5c6370;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #3e4451;
                color: #abb2bf;
                border: 1px solid #5c6370;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px; /* no border for a clean look */
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png); /* Placeholder, ensure you have a light arrow icon */
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #444;
                height: 8px;
                border-radius: 4px;
                background: #333;
            }
            QSlider::handle:horizontal {
                background: #61afef;
                border: 1px solid #444;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #61afef;
                border-radius: 4px;
            }
        """

        light_theme_content = """
            QMainWindow {
                background-color: #f0f0f0;
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #bbb;
                background: #ffffff;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #e0e0e0;
                color: #333333;
                border: 1px solid #bbb;
                border-bottom-color: #e0e0e0;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #ffffff;
                border-color: #bbb;
                border-bottom-color: #ffffff;
            }
            QTabBar::tab:hover {
                background: #d0d0d0;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                border: 1px solid #ccc;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #ffffff;
            }
            QGroupBox::title {
                color: #007bff; /* Blue */
            }
            QPushButton {
                background-color: #007bff; /* Blue */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QLineEdit {
                background-color: #f8f8f8;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #f8f8f8;
                color: #333;
                border: 1px solid #ccc;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_dark.png); /* Placeholder, ensure you have a dark arrow icon */
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #ccc;
                height: 8px;
                border-radius: 4px;
                background: #eee;
            }
            QSlider::handle:horizontal {
                background: #007bff;
                border: 1px solid #ccc;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #007bff;
                border-radius: 4px;
            }
        """

        blue_theme_content = """
            QMainWindow {
                background-color: #1a2a40; /* Dark blue */
                color: #e0f2f7; /* Light cyan text */
            }
            QTabWidget::pane {
                border: 1px solid #2b4a68;
                background: #152535;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #2e527d;
                color: #e0f2f7;
                border: 1px solid #3c6595;
                border-bottom-color: #2e527d;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #1f3d5a;
                border-color: #3c6595;
                border-bottom-color: #1f3d5a;
            }
            QTabBar::tab:hover {
                background: #3a6296;
            }
            QLabel {
                color: #e0f2f7;
            }
            QGroupBox {
                border: 1px solid #3c6595;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #1a2a40;
            }
            QGroupBox::title {
                color: #87CEEB; /* Sky Blue */
            }
            QPushButton {
                background-color: #4682B4; /* Steel Blue */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3a719d;
            }
            QLineEdit {
                background-color: #223f5b;
                color: #e0f2f7;
                border: 1px solid #4a6c8e;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #223f5b;
                color: #e0f2f7;
                border: 1px solid #4a6c8e;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png);
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #3c6595;
                height: 8px;
                border-radius: 4px;
                background: #2b4a68;
            }
            QSlider::handle:horizontal {
                background: #4682B4;
                border: 1px solid #3c6595;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #4682B4;
                border-radius: 4px;
            }
        """

        # New themes
        dark_gray_theme_content = """
            QMainWindow {
                background-color: #3c3f41; /* Darker gray */
                color: #fdfdfd; /* White */
            }
            QTabWidget::pane {
                border: 1px solid #505050;
                background: #333333;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #4a4d4f;
                color: #fdfdfd;
                border: 1px solid #505050;
                border-bottom-color: #4a4d4f;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #3c3f41;
                border-color: #505050;
                border-bottom-color: #3c3f41;
            }
            QTabBar::tab:hover {
                background: #5a5d5f;
            }
            QLabel {
                color: #fdfdfd;
            }
            QGroupBox {
                border: 1px solid #666;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #3c3f41;
            }
            QGroupBox::title {
                color: #79c0ff; /* GitHub Blue */
            }
            QPushButton {
                background-color: #6a737d; /* Grayish blue */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #586069;
            }
            QLineEdit {
                background-color: #4b4f52;
                color: #fdfdfd;
                border: 1px solid #6c7072;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #4b4f52;
                color: #fdfdfd;
                border: 1px solid #6c7072;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png);
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #505050;
                height: 8px;
                border-radius: 4px;
                background: #444;
            }
            QSlider::handle:horizontal {
                background: #6a737d;
                border: 1px solid #505050;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #6a737d;
                border-radius: 4px;
            }
        """

        forest_green_theme_content = """
            QMainWindow {
                background-color: #228B22; /* Forest Green */
                color: #FFFFFF;
            }
            QTabWidget::pane {
                border: 1px solid #4CAF50;
                background: #1B5E20;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #388E3C;
                color: #FFFFFF;
                border: 1px solid #4CAF50;
                border-bottom-color: #388E3C;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #2E7D32;
                border-color: #4CAF50;
                border-bottom-color: #2E7D32;
            }
            QTabBar::tab:hover {
                background: #4CAF50;
            }
            QLabel {
                color: #FFFFFF;
            }
            QGroupBox {
                border: 1px solid #66BB6A;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #228B22;
            }
            QGroupBox::title {
                color: #A5D6A7; /* Light Green */
            }
            QPushButton {
                background-color: #66BB6A; /* Light Green */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #4CAF50;
            }
            QLineEdit {
                background-color: #339933;
                color: #FFFFFF;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #339933;
                color: #FFFFFF;
                border: 1px solid #4CAF50;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png);
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #4CAF50;
                height: 8px;
                border-radius: 4px;
                background: #388E3C;
            }
            QSlider::handle:horizontal {
                background: #66BB6A;
                border: 1px solid #4CAF50;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #66BB6A;
                border-radius: 4px;
            }
        """

        warm_sepia_theme_content = """
            QMainWindow {
                background-color: #704214; /* Sepia Brown */
                color: #F5DEB3; /* Wheat */
            }
            QTabWidget::pane {
                border: 1px solid #8B4513;
                background: #5A2D0C;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #6C3817;
                color: #F5DEB3;
                border: 1px solid #8B4513;
                border-bottom-color: #6C3817;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #5A2D0C;
                border-color: #8B4513;
                border-bottom-color: #5A2D0C;
            }
            QTabBar::tab:hover {
                background: #8B4513;
            }
            QLabel {
                color: #F5DEB3;
            }
            QGroupBox {
                border: 1px solid #A0522D;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #704214;
            }
            QGroupBox::title {
                color: #DEB887; /* BurlyWood */
            }
            QPushButton {
                background-color: #A0522D; /* Sienna */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #8B4513;
            }
            QLineEdit {
                background-color: #7C4F2A;
                color: #F5DEB3;
                border: 1px solid #A0522D;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #7C4F2A;
                color: #F5DEB3;
                border: 1px solid #A0522D;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png);
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #A0522D;
                height: 8px;
                border-radius: 4px;
                background: #8B4513;
            }
            QSlider::handle:horizontal {
                background: #A0522D;
                border: 1px solid #A0522D;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #A0522D;
                border-radius: 4px;
            }
        """

        ocean_blue_theme_content = """
            QMainWindow {
                background-color: #003366; /* Dark Ocean Blue */
                color: #E0FFFF; /* Light Cyan */
            }
            QTabWidget::pane {
                border: 1px solid #005099;
                background: #002244;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #004488;
                color: #E0FFFF;
                border: 1px solid #005099;
                border-bottom-color: #004488;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #002244;
                border-color: #005099;
                border-bottom-color: #002244;
            }
            QTabBar::tab:hover {
                background: #005099;
            }
            QLabel {
                color: #E0FFFF;
            }
            QGroupBox {
                border: 1px solid #0066CC;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #003366;
            }
            QGroupBox::title {
                color: #87CEEB; /* Sky Blue */
            }
            QPushButton {
                background-color: #4682B4; /* Steel Blue */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #3A719D;
            }
            QLineEdit {
                background-color: #004080;
                color: #E0FFFF;
                border: 1px solid #005099;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #004080;
                color: #E0FFFF;
                border: 1px solid #005099;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png);
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #005099;
                height: 8px;
                border-radius: 4px;
                background: #004488;
            }
            QSlider::handle:horizontal {
                background: #4682B4;
                border: 1px solid #005099;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #4682B4;
                border-radius: 4px;
            }
        """

        vibrant_purple_theme_content = """
            QMainWindow {
                background-color: #4B0082; /* Indigo */
                color: #E6E6FA; /* Lavender */
            }
            QTabWidget::pane {
                border: 1px solid #6A0DAD;
                background: #300050;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #5A1F8D;
                color: #E6E6FA;
                border: 1px solid #6A0DAD;
                border-bottom-color: #5A1F8D;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #300050;
                border-color: #6A0DAD;
                border-bottom-color: #300050;
            }
            QTabBar::tab:hover {
                background: #6A0DAD;
            }
            QLabel {
                color: #E6E6FA;
            }
            QGroupBox {
                border: 1px solid #8A2BE2; /* Blue Violet */
                border-radius: 8px;
                margin-top: 10px;
                background-color: #4B0082;
            }
            QGroupBox::title {
                color: #DDA0DD; /* Plum */
            }
            QPushButton {
                background-color: #8A2BE2; /* Blue Violet */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #7B1BE0;
            }
            QLineEdit {
                background-color: #5F2A80;
                color: #E6E6FA;
                border: 1px solid #8A2BE2;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #5F2A80;
                color: #E6E6FA;
                border: 1px solid #8A2BE2;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png);
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #8A2BE2;
                height: 8px;
                border-radius: 4px;
                background: #6A0DAD;
            }
            QSlider::handle:horizontal {
                background: #8A2BE2;
                border: 1px solid #8A2BE2;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #8A2BE2;
                border-radius: 4px;
            }
        """

        light_modern_theme_content = """
            QMainWindow {
                background-color: #E0E0E0; /* Light Gray */
                color: #333333;
            }
            QTabWidget::pane {
                border: 1px solid #C0C0C0;
                background: #F8F8F8;
                border-radius: 8px;
            }
            QTabBar::tab {
                background: #D0D0D0;
                color: #333333;
                border: 1px solid #C0C0C0;
                border-bottom-color: #D0D0D0;
                border-top-left-radius: 5px;
                border-top-right-radius: 5px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #F8F8F8;
                border-color: #C0C0C0;
                border-bottom-color: #F8F8F8;
            }
            QTabBar::tab:hover {
                background: #E8E8E8;
            }
            QLabel {
                color: #333333;
            }
            QGroupBox {
                border: 1px solid #A0A0A0;
                border-radius: 8px;
                margin-top: 10px;
                background-color: #F8F8F8;
            }
            QGroupBox::title {
                color: #555555; /* Darker Gray */
            }
            QPushButton {
                background-color: #607D8B; /* Blue Grey */
                color: white;
                border-radius: 5px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #455A64;
            }
            QLineEdit {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #C0C0C0;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox {
                background-color: #FFFFFF;
                color: #333333;
                border: 1px solid #C0C0C0;
                border-radius: 4px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_dark.png);
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 1px solid #C0C0C0;
                height: 8px;
                border-radius: 4px;
                background: #E8E8E8;
            }
            QSlider::handle:horizontal {
                background: #607D8B;
                border: 1px solid #C0C0C0;
                width: 20px;
                margin: -6px 0;
                border-radius: 10px;
            }
            QSlider::sub-page:horizontal {
                background: #607D8B;
                border-radius: 4px;
            }
        """

        high_contrast_theme_content = """
            QMainWindow {
                background-color: #000000; /* Black */
                color: #FFFF00; /* Yellow */
            }
            QTabWidget::pane {
                border: 2px solid #FF00FF; /* Magenta border */
                background: #111111;
                border-radius: 0px; /* Sharp corners */
            }
            QTabBar::tab {
                background: #333333;
                color: #00FF00; /* Green */
                border: 2px solid #FF00FF;
                border-bottom-color: #333333;
                border-top-left-radius: 0px;
                border-top-right-radius: 0px;
                padding: 6px 12px;
            }
            QTabBar::tab:selected {
                background: #000000;
                border-color: #FF00FF;
                border-bottom-color: #000000;
            }
            QTabBar::tab:hover {
                background: #222222;
            }
            QLabel {
                color: #FFFF00;
            }
            QGroupBox {
                border: 2px solid #00FFFF; /* Cyan */
                border-radius: 0px;
                margin-top: 10px;
                background-color: #000000;
            }
            QGroupBox::title {
                color: #FF0000; /* Red */
            }
            QPushButton {
                background-color: #FF00FF; /* Magenta */
                color: white;
                border-radius: 0px;
                padding: 8px 15px;
            }
            QPushButton:hover {
                background-color: #CC00CC;
            }
            QLineEdit {
                background-color: #222222;
                color: #FFFF00;
                border: 2px solid #FF00FF;
                border-radius: 0px;
                padding: 4px;
            }
            QComboBox {
                background-color: #222222;
                color: #FFFF00;
                border: 2px solid #FF00FF;
                border-radius: 0px;
                padding: 4px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png);
                width: 16px;
                height: 16px;
            }
            QSlider::groove:horizontal {
                border: 2px solid #FF00FF;
                height: 8px;
                border-radius: 0px;
                background: #333;
            }
            QSlider::handle:horizontal {
                background: #FFFF00;
                border: 2px solid #FF00FF;
                width: 20px;
                margin: -6px 0;
                border-radius: 0px;
            }
            QSlider::sub-page:horizontal {
                background: #FFFF00;
                border-radius: 0px;
            }
        """


        themes_to_create = {
            "dark_theme": dark_theme_content,
            "light_theme": light_theme_content,
            "blue_theme": blue_theme_content,
            "dark_gray_theme": dark_gray_theme_content,
            "forest_green_theme": forest_green_theme_content,
            "warm_sepia_theme": warm_sepia_theme_content,
            "ocean_blue_theme": ocean_blue_theme_content,
            "vibrant_purple_theme": vibrant_purple_theme_content,
            "light_modern_theme": light_modern_theme_content,
            "high_contrast_theme": high_contrast_theme_content
        }

        for theme_name, content in themes_to_create.items():
            file_path = os.path.join(theme_dir, theme_name + ".qss")
            if not os.path.exists(file_path):
                try:
                    with open(file_path, 'w') as f:
                        f.write(content)
                    self.logger.info("Created default theme file: {}".format(file_path))
                except Exception as e:
                    self.logger.error("Failed to create default theme file {}: {}".format(file_path, e))

    def _apply_selected_theme(self):
        """Applies the theme selected in the combo box to the main window."""
        selected_theme = self.theme_combo.currentText()
        # Correctly call the private method _apply_theme on the main_window_ref
        if hasattr(self.main_window_ref, '_apply_theme'):
            self.main_window_ref._apply_theme(selected_theme)
            # Emit the signal after successfully applying the theme
            self.theme_changed.emit(selected_theme) 
            self.logger.info("Theme '{}' applied and theme_changed signal emitted.".format(selected_theme))
        else:
            self.logger.error("Main window reference does not have '_apply_theme' method or it's not accessible.")

    def _apply_selected_sensor_display_type(self):
        """Applies the selected sensor display type to the main window configuration."""
        selected_type = self.sensor_type_combo.currentText()
        self.config.set_setting("sensor_display_type", selected_type)
        self.logger.info("Sensor display type set to: {}".format(selected_type))
        self.sensor_display_type_changed.emit(selected_type) # Emit new signal
        # Re-apply theme to trigger all tabs to redraw their gauges with the new type
        if hasattr(self.main_window_ref, '_apply_theme'):
            current_theme = self.config.get_setting("current_theme", "dark_theme")
            self.main_window_ref._apply_theme(current_theme) # Re-apply current theme to trigger tab updates


    def set_style(self):
        """Applies specific styling for the tab."""
        self.setStyleSheet("""
            QWidget#UICustomizationTab {
                background-color: transparent;
            }
            QLabel#uiCustomizationTabTitleLabel, QLabel#themeLabel {
                color: %s; /* Dynamic color for labels */
            }
            QFrame#contentFrame {
                border: 1px solid %s; /* Dynamic border color */
                border-radius: 15px;
                background-color: %s; /* Dynamic background color */
                padding: 20px;
                min-width: 400px;
                max-width: 600px;
            }
            QComboBox {
                background-color: %s; /* Dynamic background from theme_palette */
                color: %s; /* Dynamic text color from theme_palette */
                border: 1px solid %s; /* Dynamic border color from theme_palette */
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png); /* Assume light arrow for dark backgrounds */
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView { /* Style for the dropdown list */
                background-color: %s; /* Same as combo box background */
                color: %s; /* Same as combo box text color */
                selection-background-color: %s; /* Highlight color */
                selection-color: %s; /* Highlighted text color */
                border: 1px solid %s; /* Border for the dropdown */
            }
            QPushButton {
                background-color: %s; /* Dynamic button background from theme_palette */
                color: %s; /* Dynamic button text color from theme_palette */
                border-radius: 10px;
                padding: 10px 20px;
            }
            QPushButton:hover {
                background-color: #1A8B86; /* Static hover, consider making dynamic if needed */
            }
        """ % (
            self.theme_palette["label_color"].name(), # Label color
            self.theme_palette["frame_border"].name(), # Frame border
            self.theme_palette["frame_bg"].name(), # Frame background
            self.theme_palette["combo_bg"].name(),
            self.theme_palette["combo_text"].name(),
            self.theme_palette["combo_border"].name(),
            self.theme_palette["combo_bg"].name(), # Dropdown background
            self.theme_palette["combo_text"].name(), # Dropdown text
            self.theme_palette["button_bg"].name(), # Assuming button_bg for selection highlight
            self.theme_palette["button_text"].name(), # Assuming button_text for selected item color
            self.theme_palette["combo_border"].name(), # Dropdown border
            self.theme_palette["button_bg"].name(),
            self.theme_palette["button_text"].name()
        ))
