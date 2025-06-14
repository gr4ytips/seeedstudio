# ui/environment_sensors_tab.py
import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QFrame, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QColor

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from ui.gauge_widget import GaugeWidget
from ui.gui_widgetsone import GaugeWidgetOne
from ui.gui_widgets_multiring import GaugeWidgetMultiRing
from utils.logger import Logger
from utils.config_manager import ConfigManager

class EnvironmentSensorsTab(QWidget):
    """
    Separate tab to display Temperature and Humidity sensors.
    """
    def __init__(self, sensor_manager, parent=None):
        super(EnvironmentSensorsTab, self).__init__(parent)
        self.logger = Logger.get_logger()
        self.sensor_manager = sensor_manager
        self.config = ConfigManager.get_instance()

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        
        # Set the size policy for the tab itself to expand in both directions.
        # This ensures the tab will try to fill all available space given by its parent (QTabWidget).
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Initialize gauge placeholders
        self.temp_gauge = None
        self.hum_gauge = None
        self.content_layout = None # Will be set in _setup_ui

        self._setup_ui()
        # Initial call to _create_gauges will build them based on current config
        self._create_gauges() 
        self._set_theme_colors() # Set initial theme colors and apply to gauges
        self.set_style() # Apply the overall stylesheet for the tab and its frame
        self.logger.info("EnvironmentSensorsTab initialized.")

    def _setup_ui(self):
        """Sets up the UI elements for the environment sensors tab."""
        # Main title label for the tab
        self.title_label = QLabel("Environment Sensors: DHT Temperature & Humidity")
        self.title_label.setObjectName("environmentTabTitleLabel") # For specific QSS targeting
        self.title_label.setFont(QFont("Inter", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setContentsMargins(0, 20, 0, 20) # Add some top/bottom padding
        
        # Add the title label to the main vertical layout
        self.main_layout.addWidget(self.title_label)
        
        # Create a QFrame to contain the gauges. This frame will have the themed background.
        self.content_frame = QFrame(self)
        self.content_frame.setFrameShape(QFrame.StyledPanel)
        self.content_frame.setFrameShadow(QFrame.Raised)
        self.content_frame.setObjectName("contentFrame") # For specific QSS targeting
        
        # Set the size policy for the content frame to expand. This is crucial for it to fill space.
        self.content_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Create a horizontal layout inside the content frame to hold the gauges
        self.content_layout = QHBoxLayout(self.content_frame) # Store reference to content_layout
        self.content_layout.setAlignment(Qt.AlignCenter) # Keep gauges centered within the frame

        # Add the content frame to the main layout. It will expand due to its size policy.
        self.main_layout.addWidget(self.content_frame)
        
        # Add a stretch at the bottom of the main_layout. This pushes content up and
        # ensures the content_frame takes all remaining vertical space not occupied by the title.
        self.main_layout.addStretch(1)

    def _clear_gauges(self):
        """Removes existing gauge widgets from the layout."""
        if self.content_layout is not None:
            while self.content_layout.count():
                item = self.content_layout.takeAt(0)
                if item.widget():
                    self.logger.debug("Removed old gauge: {0}".format(item.widget().title))
                    item.widget().deleteLater() # Delete the widget to free resources
                    
    def _create_gauges(self):
        """
        Creates and adds gauge widgets to the layout based on the current
        sensor_display_type setting.
        """
        self._clear_gauges() # Always clear existing gauges first before creating new ones

        sensor_display_type = self.config.get_setting("sensor_display_type", "Default Gauge")
        self.logger.info("Creating gauges with type: {0}".format(sensor_display_type))

        # Define sensor thresholds for temperature and humidity for dynamic gauge color changes
        temp_thresholds = {
            "CRITICAL_HIGH": {"value": 35, "message": "High Temperature!"},
            "WARNING_HIGH": {"value": 30, "message": "Warm Temperature"},
            "WARNING_LOW": {"value": 10, "message": "Cool Temperature"},
            "CRITICAL_LOW": {"value": 5, "message": "Very Low Temperature!"}
        }
        hum_thresholds = {
            "CRITICAL_HIGH": {"value": 80, "message": "High Humidity!"},
            "WARNING_HIGH": {"value": 70, "message": "Damp Humidity"},
            "WARNING_LOW": {"value": 30, "message": "Dry Humidity"},
            "CRITICAL_LOW": {"value": 20, "message": "Very Low Humidity!"}
        }

        # Instantiate the correct gauge type based on the configuration setting
        if sensor_display_type == "Default Gauge":
            self.temp_gauge = GaugeWidget("Temperature", "°C", 0, 50, config_manager=self.config)
            self.hum_gauge = GaugeWidget("Humidity", "%", 0, 100, config_manager=self.config)
        elif sensor_display_type == "Gauge Widget One":
            self.temp_gauge = GaugeWidgetOne("Temperature", 0, 50, "°C", sensor_thresholds=temp_thresholds, config_manager=self.config)
            self.hum_gauge = GaugeWidgetOne("Humidity", 0, 100, "%", sensor_thresholds=hum_thresholds, config_manager=self.config)
        elif sensor_display_type == "Gauge Widget Multi Ring":
            self.temp_gauge = GaugeWidgetMultiRing("Temperature", 0, 50, "°C", sensor_thresholds=temp_thresholds, config_manager=self.config)
            self.hum_gauge = GaugeWidgetMultiRing("Humidity", 0, 100, "%", sensor_thresholds=hum_thresholds, config_manager=self.config)
        else:
            # Fallback to default if an unknown type is encountered
            self.logger.warning("Unknown sensor display type: {0}. Falling back to Default Gauge.".format(sensor_display_type))
            self.temp_gauge = GaugeWidget("Temperature", "°C", 0, 50, config_manager=self.config)
            self.hum_gauge = GaugeWidget("Humidity", "%", 0, 100, config_manager=self.config)

        # Set size policy for newly created gauges to expand. This allows them to scale.
        self.temp_gauge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.hum_gauge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        # Add gauges to the content layout with equal stretch factors to distribute horizontal space.
        self.content_layout.addWidget(self.temp_gauge, stretch=1)
        self.content_layout.addSpacing(40) # Keep some visual spacing between the gauges
        self.content_layout.addWidget(self.hum_gauge, stretch=1)

        # Apply current theme colors to the newly created gauges
        self._set_theme_colors()

    def update_dht_data(self, temperature, humidity):
        """
        Updates the Temperature and Humidity gauges.
        This slot is connected to the SensorWorker's dht_data_updated signal.
        """
        # Ensure gauges exist before attempting to update their values
        if self.temp_gauge and self.hum_gauge:
            self.temp_gauge.set_value(temperature)
            self.hum_gauge.set_value(humidity)

    def _set_theme_colors(self):
        """
        Explicitly calls theme update methods on the currently active GaugeWidget instances
        within this tab to update their internal color attributes.
        Also updates labels and the content frame's background/border.
        """
        current_theme = self.config.get_setting("current_theme", "dark_theme")
        sensor_display_type = self.config.get_setting("sensor_display_type", "Default Gauge")

        # Define color palettes for various themes, specifically for this tab's elements
        # These palettes are structured to provide all necessary colors for the different gauge types
        theme_palettes = {
            "dark_theme": {
                "normal_text": QColor("#abb2bf"), # Light gray
                "hover_text": QColor("#FFD700"), # Gold
                "frame_background": QColor(30, 30, 30, 0.7), # Slightly transparent dark gray for the frame
                "frame_border": QColor(102, 102, 102), # Gray border for the frame
                "gauge_bg_color": "#3A3A3A", # Background for gauges
                "gauge_border_color": "#5A5A5A", # Border for gauges
                "gauge_text_color": "#E0E0E0", # Text color inside gauges
                "gauge_accent_color": "#66BB6A", # Accent color for GaugeWidgetOne
                "gauge_critical_color": "red", # Critical threshold color
                "gauge_warning_color": "orange", # Warning threshold color
                "gauge_normal_color": "#00BFFF", # Normal state color (used by Multi Ring)
                "gauge_fill_color": "#5A5A5A" # Fill color for GaugeWidgetOne
            },
            "light_theme": {
                "normal_text": QColor("#333333"),
                "hover_text": QColor("#007bff"),
                "frame_background": QColor(255, 255, 255, 0.9),
                "frame_border": QColor(204, 204, 204),
                "gauge_bg_color": "#F0F0F0",
                "gauge_border_color": "#C0C0C0",
                "gauge_text_color": "#333333",
                "gauge_accent_color": "#40A750",
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
                "normal_color": "#4682B4", # Note: 'normal_color' instead of 'gauge_normal_color' for consistency in palettes
                "gauge_normal_color": "#4682B4", # Explicitly add for GaugeWidgetMultiRing usage
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
                "normal_color": "#6a737d", # Note: 'normal_color'
                "gauge_normal_color": "#6a737d", # Explicitly add
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
                "normal_color": "#66BB6A", # Note: 'normal_color'
                "gauge_normal_color": "#66BB6A", # Explicitly add
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
                "normal_color": "#A0522D", # Note: 'normal_color'
                "gauge_normal_color": "#A0522D", # Explicitly add
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
                "normal_color": "#4682B4", # Note: 'normal_color'
                "gauge_normal_color": "#4682B4", # Explicitly add
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
                "normal_color": "#8A2BE2", # Note: 'normal_color'
                "gauge_normal_color": "#8A2BE2", # Explicitly add
                "gauge_fill_color": "#5A1F8D"
            },
            "light_modern_theme": {
                "normal_text": QColor("#333333"),
                "hover_text": QColor("#555555"),
                "frame_background": QColor(224, 224, 224, 0.7),
                "frame_border": QColor(160, 160, 160),
                "gauge_bg_color": "#F8F8F8",
                "gauge_border_color": "#C0C0C0",
                "gauge_text_color": "#333333",
                "gauge_accent_color": "#607D8B",
                "gauge_critical_color": "#CC0000",
                "gauge_warning_color": "#E5A000",
                "normal_color": "#607D8B", # Note: 'normal_color'
                "gauge_normal_color": "#607D8B", # Explicitly add
                "gauge_fill_color": "#D0D0D0"
            },
            "high_contrast_theme": {
                "normal_text": QColor("#FFFF00"),
                "hover_text": QColor("#00FF00"),
                "frame_background": QColor(0, 0, 0, 0.9),
                "frame_border": QColor(0, 255, 255),
                "gauge_bg_color": "#111111",
                "gauge_border_color": "#FF00FF",
                "gauge_text_color": "#FFFF00",
                "gauge_accent_color": "#00FF00",
                "gauge_critical_color": "#FF0000",
                "gauge_warning_color": "#FFA500",
                "normal_color": "#00FF00", # Note: 'normal_color'
                "gauge_normal_color": "#00FF00", # Explicitly add
                "gauge_fill_color": "#333333"
            }
        }

        # Retrieve the palette for the current theme, defaulting to dark_theme if not found
        palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"])
        
        # Update internal color attributes for the tab's QSS
        self.normal_text_color = palette["normal_text"]
        self.hover_text_color = palette["hover_text"]
        self.frame_background_color = QColor(palette["frame_background"])
        self.frame_border_color = QColor(palette["frame_border"])
        
        # Apply QSS directly to the title label to update its color
        self.title_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))

        # Apply theme colors to the gauge widgets if they have been instantiated
        if self.temp_gauge and self.hum_gauge:
            if sensor_display_type == "Default Gauge":
                # Default GaugeWidget has its own _set_theme_colors method
                self.temp_gauge._set_theme_colors()
                self.hum_gauge._set_theme_colors()
            elif sensor_display_type in ["Gauge Widget One", "Gauge Widget Multi Ring"]:
                # These custom gauge widgets have a 'set_theme_colors' method that takes specific parameters
                self.temp_gauge.set_theme_colors(
                    palette["gauge_bg_color"], 
                    palette["gauge_border_color"], 
                    palette["gauge_text_color"], 
                    palette["gauge_accent_color"],
                    palette["gauge_critical_color"],
                    palette["gauge_warning_color"],
                    # Use 'gauge_normal_color' if present, otherwise fallback to 'normal_color' or accent
                    palette.get("gauge_normal_color", palette.get("normal_color", palette["gauge_accent_color"])),
                    palette["gauge_fill_color"]
                )
                self.hum_gauge.set_theme_colors(
                    palette["gauge_bg_color"], 
                    palette["gauge_border_color"], 
                    palette["gauge_text_color"], 
                    palette["gauge_accent_color"],
                    palette["gauge_critical_color"],
                    palette["gauge_warning_color"],
                    palette.get("gauge_normal_color", palette.get("normal_color", palette["gauge_accent_color"])),
                    palette["gauge_fill_color"]
                )

        # Re-apply the overall QSS for the tab and its content frame to ensure colors are updated
        self.set_style()

    def set_style(self):
        """Applies specific styling for the tab using themed colors."""
        self.setStyleSheet("""
            QWidget#EnvironmentSensorsTab {{
                /* The background of the tab itself is transparent, allowing the main window's background to show */
                background-color: transparent;
            }}
            QLabel#environmentTabTitleLabel {{ /* Style for the main title label in this tab */
                color: {normal_text_color};
            }}
            QFrame#contentFrame {{ /* Style for the frame containing the gauges */
                border: 1px solid {frame_border_color};
                border-radius: 15px;
                background-color: {frame_background_color};
                padding: 20px;
                /* min-width and max-width removed to allow the frame to be fully responsive */
            }}
            QLabel {{ /* General QLabel style within this tab, if not overridden by specific objectNames */
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
