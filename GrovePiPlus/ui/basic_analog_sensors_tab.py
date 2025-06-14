# ui/basic_analog_sensors_tab.py
import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy # Import QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor # Import QColor

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from ui.gauge_widget import GaugeWidget
from ui.gui_widgetsone import GaugeWidgetOne # Import the new GaugeWidgetOne
from ui.gui_widgets_multiring import GaugeWidgetMultiRing # Import the new GaugeWidgetMultiRing
from utils.logger import Logger
from utils.config_manager import ConfigManager # Import ConfigManager

class BasicAnalogSensorsTab(QWidget):
    """
    Separate tab to display Ultrasonic, Sound, and Light sensors.
    """
    def __init__(self, sensor_manager, parent=None):
        super(BasicAnalogSensorsTab, self).__init__(parent)
        self.logger = Logger.get_logger()
        self.sensor_manager = sensor_manager
        self.config = ConfigManager.get_instance() # Get config instance here

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        
        # Set size policy for the tab itself to expand, allowing it to fill its parent's space
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialize gauge placeholders
        self.ultrasonic_gauge = None
        self.sound_gauge = None
        self.light_gauge = None
        self.content_layout = None # Will be set in _setup_ui

        self._setup_ui()
        # Initial call to _create_gauges will build them based on current config
        self._create_gauges()
        self._set_theme_colors() # Set initial theme colors
        self.set_style()
        self.logger.info("BasicAnalogSensorsTab initialized.")

    def _setup_ui(self):
        """Sets up the UI elements for the basic analog sensors tab."""
        # Use an objectName for the title label for consistent styling via QSS or direct manipulation
        self.title_label = QLabel("Basic Analog Sensors: Ultrasonic, Sound, Light")
        self.title_label.setObjectName("basicAnalogTabTitleLabel") # Add object name
        self.title_label.setFont(QFont("Inter", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setContentsMargins(0, 20, 0, 20)
        self.main_layout.addWidget(self.title_label)

        # Use an objectName for the content frame for consistent styling
        self.content_frame = QFrame(self)
        self.content_frame.setFrameShape(QFrame.StyledPanel)
        self.content_frame.setFrameShadow(QFrame.Raised)
        self.content_frame.setObjectName("contentFrame")
        
        # Set size policy for the content frame to expand
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.content_layout = QHBoxLayout(self.content_frame) # Store reference to content_layout
        self.content_layout.setAlignment(Qt.AlignCenter)

        self.main_layout.addWidget(self.content_frame, stretch=1) # Give content frame all available vertical stretch

    def _clear_gauges(self):
        """Removes existing gauge widgets from the layout."""
        if self.content_layout is not None:
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                if item.widget():
                    # Fix: Changed f-string to .format() for Python 3.5 compatibility
                    self.logger.debug("Removed old gauge: {0}".format(item.widget().title))
                    item.widget().deleteLater() # Delete the widget to free resources

    def _create_gauges(self):
        """
        Creates and adds gauge widgets to the layout based on the current
        sensor_display_type setting.
        """
        self._clear_gauges() # Always clear existing gauges first

        sensor_display_type = self.config.get_setting("sensor_display_type", "Default Gauge")
        # Fix: Changed f-string to .format() for Python 3.5 compatibility
        self.logger.info("Creating gauges with type: {0}".format(sensor_display_type))

        # Add stretch to content layout to ensure gauges spread out if space allows
        self.content_layout.addStretch(1) 

        if sensor_display_type == "Default Gauge":
            self.ultrasonic_gauge = GaugeWidget("Ultrasonic", "cm", 0, 300, config_manager=self.config)
            self.sound_gauge = GaugeWidget("Sound", "raw", 0, 1023, config_manager=self.config)
            self.light_gauge = GaugeWidget("Light", "raw", 0, 1023, config_manager=self.config)
        elif sensor_display_type == "Gauge Widget One":
            # Pass config_manager to GaugeWidgetOne for theme awareness
            self.ultrasonic_gauge = GaugeWidgetOne("Ultrasonic", 0, 300, "cm", config_manager=self.config)
            self.sound_gauge = GaugeWidgetOne("Sound", 0, 1023, "Raw", config_manager=self.config)
            self.light_gauge = GaugeWidgetOne("Light", 0, 1023, "Raw", config_manager=self.config)
        elif sensor_display_type == "Gauge Widget Multi Ring":
            # Pass config_manager to GaugeWidgetMultiRing for theme awareness
            self.ultrasonic_gauge = GaugeWidgetMultiRing("Ultrasonic", 0, 300, "cm", config_manager=self.config)
            self.sound_gauge = GaugeWidgetMultiRing("Sound", 0, 1023, "Raw", config_manager=self.config)
            self.light_gauge = GaugeWidgetMultiRing("Light", 0, 1023, "Raw", config_manager=self.config)
        else:
            # Fallback to default if an unknown type is encountered
            # Fix: Changed f-string to .format() for Python 3.5 compatibility
            self.logger.warning("Unknown sensor display type: {0}. Falling back to Default Gauge.".format(sensor_display_type))
            self.ultrasonic_gauge = GaugeWidget("Ultrasonic", "cm", 0, 300, config_manager=self.config)
            self.sound_gauge = GaugeWidget("Sound", "raw", 0, 1023, config_manager=self.config)
            self.light_gauge = GaugeWidget("Light", "raw", 0, 1023, config_manager=self.config)

        # Set size policy to expanding for responsive resizing
        self.ultrasonic_gauge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.sound_gauge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.light_gauge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Set reasonable minimum sizes for the gauges
        self.ultrasonic_gauge.setMinimumSize(120, 120)
        self.sound_gauge.setMinimumSize(120, 120)
        self.light_gauge.setMinimumSize(120, 120)

        self.content_layout.addWidget(self.ultrasonic_gauge)
        self.content_layout.addSpacing(20)
        self.content_layout.addWidget(self.sound_gauge)
        self.content_layout.addSpacing(20)
        self.content_layout.addWidget(self.light_gauge)
        self.content_layout.addStretch(1) # Add stretch after the gauges as well

        # Apply current theme colors to the newly created gauges
        self._set_theme_colors()


    def update_ultrasonic_data(self, distance):
        """Updates the Ultrasonic gauge."""
        if self.ultrasonic_gauge:
            self.ultrasonic_gauge.set_value(distance)

    def update_sound_data(self, raw_value):
        """Updates the Sound gauge."""
        if self.sound_gauge:
            self.sound_gauge.set_value(raw_value)

    def update_light_data(self, raw_value):
        """Updates the Light gauge."""
        if self.light_gauge:
            self.light_gauge.set_value(raw_value)

    def _set_theme_colors(self):
        """Sets internal color attributes based on the current theme for dynamic elements."""
        current_theme = self.config.get_setting("current_theme", "dark_theme")
        sensor_display_type = self.config.get_setting("sensor_display_type", "Default Gauge")


        # Define color palettes for various themes, specifically for this tab's elements
        theme_palettes = {
            "dark_theme": {
                "normal_text": QColor("#abb2bf"), # Light gray
                "hover_text": QColor("#FFD700"), # Gold
                "frame_background": QColor(30, 30, 30, 0.7),
                "frame_border": QColor(102, 102, 102), # #666
                "gauge_bg_color": "#3A3A3A", # GaugeWidgetOne/MultiRing
                "gauge_border_color": "#5A5A5A", # GaugeWidgetOne/MultiRing
                "gauge_text_color": "#E0E0E0", # GaugeWidgetOne/MultiRing
                "gauge_accent_color": "#66BB6A", # GaugeWidgetOne
                "gauge_critical_color": "red", # GaugeWidgetOne/MultiRing
                "gauge_warning_color": "orange", # GaugeWidgetOne/MultiRing
                "gauge_normal_color": "#00BFFF", # GaugeWidgetMultiRing uses this, GaugeWidgetOne uses #66BB6A
                "gauge_fill_color": "#5A5A5A" # GaugeWidgetOne
            },
            "light_theme": {
                "normal_text": QColor("#333333"),
                "hover_text": QColor("#007bff"),
                "frame_background": QColor(255, 255, 255, 0.9),
                "frame_border": QColor(204, 204, 204), # #CCC
                "gauge_bg_color": "#F0F0F0",
                "gauge_border_color": "#C0C0C0",
                "gauge_text_color": "#333333",
                "gauge_accent_color": "#40A750", # Darker green for light theme
                "gauge_critical_color": "#CC0000",
                "gauge_warning_color": "#E5A000",
                "gauge_normal_color": "#007bff",
                "gauge_fill_color": "#E0E0E0"
            },
            "blue_theme": {
                "normal_text": QColor("#e0f2f7"),
                "hover_text": QColor("#87CEEB"),
                "frame_background": QColor(26, 42, 64, 0.7),
                "frame_border": QColor(60, 101, 149),
                "gauge_bg_color": "#264264",
                "gauge_border_color": "#3c6595",
                "gauge_text_color": "#e0f2f7",
                "gauge_accent_color": "#4682B4",
                "gauge_critical_color": "#E74C3C",
                "gauge_warning_color": "#F39C12",
                "gauge_normal_color": "#4682B4",
                "gauge_fill_color": "#2B4A68"
            },
            "dark_gray_theme": {
                "normal_text": QColor("#fdfdfd"),
                "hover_text": QColor("#79c0ff"),
                "frame_background": QColor(40, 40, 40, 0.7),
                "frame_border": QColor(90, 90, 90),
                "gauge_bg_color": "#4B4F52",
                "gauge_border_color": "#6C7072",
                "gauge_text_color": "#fdfdfd",
                "gauge_accent_color": "#6a737d",
                "gauge_critical_color": "#E74C3C",
                "gauge_warning_color": "#F39C12",
                "gauge_normal_color": "#6a737d",
                "gauge_fill_color": "#4a4d4f"
            },
            "forest_green_theme": {
                "normal_text": QColor("#FFFFFF"),
                "hover_text": QColor("#9ACD32"),
                "frame_background": QColor(30, 80, 30, 0.7),
                "frame_border": QColor(60, 120, 60),
                "gauge_bg_color": "#2E7D32",
                "gauge_border_color": "#4CAF50",
                "gauge_text_color": "#FFFFFF",
                "gauge_accent_color": "#66BB6A",
                "gauge_critical_color": "#E74C3C",
                "gauge_warning_color": "#F39C12",
                "gauge_normal_color": "#66BB6A",
                "gauge_fill_color": "#388E3C"
            },
            "warm_sepia_theme": {
                "normal_text": QColor("#F5DEB3"),
                "hover_text": QColor("#DEB887"),
                "frame_background": QColor(80, 50, 30, 0.7),
                "frame_border": QColor(120, 90, 60),
                "gauge_bg_color": "#5A2D0C",
                "gauge_border_color": "#A0522D",
                "gauge_text_color": "#F5DEB3",
                "gauge_accent_color": "#A0522D",
                "gauge_critical_color": "#D35400",
                "gauge_warning_color": "#F39C12",
                "gauge_normal_color": "#A0522D",
                "gauge_fill_color": "#6C3817"
            },
            "ocean_blue_theme": {
                "normal_text": QColor("#E0FFFF"),
                "hover_text": QColor("#87CEEB"),
                "frame_background": QColor(30, 70, 120, 0.7),
                "frame_border": QColor(50, 100, 180),
                "gauge_bg_color": "#002244",
                "gauge_border_color": "#005099",
                "gauge_text_color": "#E0FFFF",
                "gauge_accent_color": "#4682B4",
                "gauge_critical_color": "#E74C3C",
                "gauge_warning_color": "#F39C12",
                "gauge_normal_color": "#4682B4",
                "gauge_fill_color": "#004488"
            },
            "vibrant_purple_theme": {
                "normal_text": QColor("#E6E6FA"),
                "hover_text": QColor("#DDA0DD"),
                "frame_background": QColor(60, 20, 100, 0.7),
                "frame_border": QColor(100, 50, 150),
                "gauge_bg_color": "#300050",
                "gauge_border_color": "#8A2BE2",
                "gauge_text_color": "#E6E6FA",
                "gauge_accent_color": "#8A2BE2",
                "gauge_critical_color": "#E74C3C",
                "gauge_warning_color": "#F39C12",
                "gauge_normal_color": "#8A2BE2",
                "gauge_fill_color": "#5A1F8D"
            },
            "light_modern_theme": {
                "normal_text": QColor("#333333"),
                "hover_text": QColor("#555555"),
                "frame_background": QColor(255, 255, 255, 0.9),
                "frame_border": QColor(160, 160, 160),
                "gauge_bg_color": "#F8F8F8",
                "gauge_border_color": "#C0C0C0",
                "gauge_text_color": "#333333",
                "gauge_accent_color": "#607D8B",
                "gauge_critical_color": "#CC0000",
                "gauge_warning_color": "#E5A000",
                "gauge_normal_color": "#607D8B",
                "gauge_fill_color": "#D0D0D0"
            },
            "high_contrast_theme": {
                "normal_text": QColor("#FFFF00"), # Yellow
                "hover_text": QColor("#00FF00"), # Green
                "frame_background": QColor(0, 0, 0, 0.9),
                "frame_border": QColor(0, 255, 255), # Cyan
                "gauge_bg_color": "#111111",
                "gauge_border_color": "#FF00FF",
                "gauge_text_color": "#FFFF00",
                "gauge_accent_color": "#00FF00",
                "gauge_critical_color": "#FF0000",
                "gauge_warning_color": "#FFA500",
                "gauge_normal_color": "#00FF00",
                "gauge_fill_color": "#333333"
            }
        }

        palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"]) # Fallback to dark
        
        self.normal_text_color = palette["normal_text"]
        self.hover_text_color = palette["hover_text"]
        self.frame_background_color = QColor(palette["frame_background"]) # Ensure QColor
        self.frame_border_color = QColor(palette["frame_border"]) # Ensure QColor

        # Apply theme colors to gauges if they exist and have the method
        if self.ultrasonic_gauge and self.sound_gauge and self.light_gauge:
            if sensor_display_type == "Default Gauge":
                self.ultrasonic_gauge._set_theme_colors()
                self.sound_gauge._set_theme_colors()
                self.light_gauge._set_theme_colors()
            elif sensor_display_type in ["Gauge Widget One", "Gauge Widget Multi Ring"]:
                # Ensure the config_manager is passed or that the set_theme_colors
                # method is called on the gauge instances with the correct palette.
                # Here, we directly call set_theme_colors with the palette values.
                self.ultrasonic_gauge.set_theme_colors(
                    palette["gauge_bg_color"], 
                    palette["gauge_border_color"], 
                    palette["gauge_text_color"], 
                    palette["gauge_accent_color"],
                    palette["gauge_critical_color"],
                    palette["gauge_warning_color"],
                    palette["gauge_normal_color"],
                    palette["gauge_fill_color"]
                )
                self.sound_gauge.set_theme_colors(
                    palette["gauge_bg_color"], 
                    palette["gauge_border_color"], 
                    palette["gauge_text_color"], 
                    palette["gauge_accent_color"],
                    palette["gauge_critical_color"],
                    palette["gauge_warning_color"],
                    palette["gauge_normal_color"],
                    palette["gauge_fill_color"]
                )
                self.light_gauge.set_theme_colors(
                    palette["gauge_bg_color"], 
                    palette["gauge_border_color"], 
                    palette["gauge_text_color"], 
                    palette["gauge_accent_color"],
                    palette["gauge_critical_color"],
                    palette["gauge_warning_color"],
                    palette["gauge_normal_color"],
                    palette["gauge_fill_color"]
                )

        # Re-apply QSS for the tab and its frame
        self.set_style()


    def set_style(self):
        """Applies specific styling for the tab using themed colors."""
        self.setStyleSheet("""
            QWidget#BasicAnalogSensorsTab {{
                background-color: transparent; /* Main window stylesheet will cover this */
            }}
            QLabel#basicAnalogTabTitleLabel {{ /* Specific style for the main title label */
                color: {normal_text_color};
            }}
            QFrame#contentFrame {{
                border: 1px solid {frame_border_color};
                border-radius: 15px;
                background-color: {frame_background_color};
                padding: 20px;
                /* Removed min-width and max-width for responsiveness */
            }}
            QLabel {{ /* General QLabel style within this tab */
                color: {normal_text_color};
            }}
            QLabel:hover {{
                color: {hover_text_color};
            }}
        """.format(
            normal_text_color=self.normal_text_color.name(),
            hover_text_color=self.hover_text_color.name(),
            frame_border_color=self.frame_border_color.name(),
            frame_background_color=self.frame_background_color.name()
        ))
