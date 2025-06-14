# ui/dashboard_tab.py
import os
import sys
from PyQt5.QtWidgets import QWidget, QGridLayout, QVBoxLayout, QLabel, QFrame, QHBoxLayout
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from ui.gauge_widget import GaugeWidget
from ui.led_bar_widget import LEDBarWidget
from utils.logger import Logger
from utils.weather_api import WeatherAPI
from utils.config_manager import ConfigManager

class DashboardTab(QWidget):
    """
    Dashboard tab displaying a 2x2 grid of sensor data and a weather widget.
    """
    def __init__(self, sensor_manager, parent=None):
        super(DashboardTab, self).__init__(parent)
        self.logger = Logger.get_logger()
        self.config = ConfigManager.get_instance()
        self.sensor_manager = sensor_manager
        self.weather_api = WeatherAPI()

        self.main_layout = QGridLayout(self)
        self.setLayout(self.main_layout)

        self._setup_environment_sensors_grid()
        self._setup_basic_analog_sensors_grid()
        self._setup_interactive_control_sensors_grid()
        self._setup_weather_widget()

        self.set_style()
        self.logger.info("DashboardTab initialized.")

    def _setup_environment_sensors_grid(self):
        """Sets up the Environment Sensors group (DHT)."""
        env_frame, env_layout = self._create_group_frame("Environment Sensors") # Get frame and its layout

        # Pass config_manager to GaugeWidget for theme awareness
        self.dht_temp_gauge = GaugeWidget("Temperature", "°C", 0, 50, config_manager=self.config)
        self.dht_hum_gauge = GaugeWidget("Humidity", "%", 0, 100, config_manager=self.config)
        
        # Use QHBoxLayout for gauges within the group frame
        gauge_layout = QHBoxLayout()
        gauge_layout.addWidget(self.dht_temp_gauge)
        gauge_layout.addWidget(self.dht_hum_gauge)
        
        env_layout.addLayout(gauge_layout)
        self.main_layout.addWidget(env_frame, 0, 0)

    def _setup_basic_analog_sensors_grid(self):
        """Sets up the Basic Analog Sensors group (Ultrasonic, Sound, Light)."""
        analog_frame, analog_layout = self._create_group_frame("Basic Analog Sensors") # Get frame and its layout

        # Pass config_manager to GaugeWidget for theme awareness
        self.ultrasonic_gauge = GaugeWidget("Ultrasonic", "cm", 0, 300, config_manager=self.config)
        self.sound_gauge = GaugeWidget("Sound", "raw", 0, 1023, config_manager=self.config)
        self.light_gauge = GaugeWidget("Light", "raw", 0, 1023, config_manager=self.config)

        gauge_layout = QHBoxLayout()
        gauge_layout.addWidget(self.ultrasonic_gauge)
        gauge_layout.addWidget(self.sound_gauge)
        gauge_layout.addWidget(self.light_gauge)

        analog_layout.addLayout(gauge_layout)
        self.main_layout.addWidget(analog_frame, 0, 1)

    def _setup_interactive_control_sensors_grid(self):
        """Sets up the Interactive Control Sensors group (Button, Relay, LED Bar, Rotary Angle)."""
        interactive_frame, interactive_layout_base = self._create_group_frame("Interactive Control Sensors") # Get frame and its layout
        # The base layout returned from _create_group_frame is a QVBoxLayout.
        # We need a QGridLayout for this section, so we'll add the grid layout
        # as a sub-layout to the base QVBoxLayout.
        
        interactive_grid_layout = QGridLayout() # Create the specific grid layout for this section

        # Button Status
        self.button_label = QLabel("Button: OFF")
        self.button_label.setAlignment(Qt.AlignCenter)
        self.button_label.setFont(QFont("Inter", 14, QFont.Bold))
        interactive_grid_layout.addWidget(self.button_label, 0, 0, 1, 2) # Span 2 columns

        # Relay Status (Display only, control is in InteractiveControlSensorsTab)
        self.relay_status_label = QLabel("Relay: OFF")
        self.relay_status_label.setAlignment(Qt.AlignCenter)
        self.relay_status_label.setFont(QFont("Inter", 14, QFont.Bold))
        interactive_grid_layout.addWidget(self.relay_status_label, 1, 0, 1, 2)

        # LED Bar (Display only)
        self.led_bar_dashboard_widget = LEDBarWidget("LED Bar Level", segments=10)
        interactive_grid_layout.addWidget(self.led_bar_dashboard_widget, 2, 0, 1, 2) # Span 2 columns

        # Rotary Angle Gauge
        self.rotary_angle_gauge = GaugeWidget("Rotary Angle", "raw", 0, 1023, config_manager=self.config) # Pass config
        interactive_grid_layout.addWidget(self.rotary_angle_gauge, 0, 2, 3, 1) # Span multiple rows, right side

        interactive_layout_base.addLayout(interactive_grid_layout) # Add the grid to the base layout
        self.main_layout.addWidget(interactive_frame, 1, 0)

    def _setup_weather_widget(self):
        """Sets up the Weather Widget for the Dashboard."""
        weather_frame, weather_layout = self._create_group_frame("Current Weather") # Get frame and its layout
        weather_frame.setMinimumSize(300, 200) # Give it a reasonable minimum size

        self.weather_icon_label = QLabel()
        self.weather_icon_label.setAlignment(Qt.AlignCenter)
        self.weather_icon_label.setFixedSize(64, 64) # Standard icon size

        self.weather_temp_label = QLabel("Loading...")
        self.weather_temp_label.setAlignment(Qt.AlignCenter)
        self.weather_temp_label.setFont(QFont("Inter", 24, QFont.Bold))

        self.weather_desc_label = QLabel("")
        self.weather_desc_label.setAlignment(Qt.AlignCenter)
        self.weather_desc_label.setFont(QFont("Inter", 14))

        self.weather_details_label = QLabel("")
        self.weather_details_label.setAlignment(Qt.AlignCenter)
        self.weather_details_label.setFont(QFont("Inter", 10))

        weather_layout.addWidget(self.weather_icon_label)
        weather_layout.addWidget(self.weather_temp_label)
        weather_layout.addWidget(self.weather_desc_label)
        weather_layout.addWidget(self.weather_details_label)
        weather_layout.addStretch(1)

        self.main_layout.addWidget(weather_frame, 1, 1) # Right-most bottom corner

        self.weather_update_timer = QTimer(self)
        self.weather_update_timer.timeout.connect(self._fetch_and_update_weather)
        self.weather_update_timer.start(self.config.get_setting("weather_update_interval_ms", 300000)) # Update every 5 minutes
        self._fetch_and_update_weather() # Initial fetch

    def _fetch_and_update_weather(self):
        """Fetches current weather data and updates the widget."""
        city = self.config.get_setting("weather_city", "Frisco")
        country = self.config.get_setting("weather_country_code", "US")
        
        self.weather_temp_label.setText("Fetching...")
        self.weather_desc_label.setText("")
        self.weather_details_label.setText("")
        self.weather_icon_label.clear()

        current_weather = self.weather_api.get_current_weather(city, country)
        if current_weather:
            temp = current_weather["temperature"]
            desc = current_weather["description"].capitalize()
            humidity = current_weather["humidity"]
            wind_speed = current_weather["wind_speed"]
            icon_code = current_weather["icon"]
            city_name = current_weather["city_name"]

            self.weather_temp_label.setText("{:.1f}°C".format(temp))
            self.weather_desc_label.setText(desc)
            self.weather_details_label.setText("Humidity: {}%\nWind: {:.1f} m/s".format(humidity, wind_speed))
            
            # Fetch weather icon (if available)
            # OpenWeatherMap icons are typically at http://openweathermap.org/img/wn/10d@2x.png
            # For a local application without direct internet access for images, we need a proxy
            # or to embed common icons. For now, we'll try a generic icon, or simply rely on text.
            # If `requests` was available, we could fetch. With `urllib.request`, fetching
            # binary image data directly into QPixmap might be more complex.
            # A common approach is to map icon codes to local emoji or SVG assets if possible.
            # For simplicity, we'll try to load a placeholder if a local icon set was planned.
            # For now, let's just use text for the icon.
            icon_path = os.path.join(project_root, 'icons', 'weather', "{}.png".format(icon_code)) # Placeholder path
            if os.path.exists(icon_path):
                 pixmap = QPixmap(icon_path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                 self.weather_icon_label.setPixmap(pixmap)
            else:
                 # Fallback to emoji or simple text
                 self.weather_icon_label.setText(self._get_weather_emoji(icon_code))
                 self.weather_icon_label.setFont(QFont("Inter", 36)) # Make emoji large
            
            # Update the title of the weather frame based on fetched city
            self.findChild(QFrame, "weatherFrame").findChild(QLabel, "groupFrameTitle").setText("Current Weather in {}".format(city_name))
        else:
            self.weather_temp_label.setText("N/A")
            self.weather_desc_label.setText("Failed to load weather")
            self.weather_details_label.setText("Check API Key/Connection")
            self.weather_icon_label.setText("?")
            self.weather_icon_label.setFont(QFont("Inter", 36))
            # Update the title of the weather frame to reflect error
            self.findChild(QFrame, "weatherFrame").findChild(QLabel, "groupFrameTitle").setText("Current Weather (Error)")


    def _get_weather_emoji(self, icon_code):
        """Maps OpenWeatherMap icon codes to simple emojis."""
        # This is a simplified mapping. Full mapping is complex.
        if "01" in icon_code: return u"\u2600" # Sun
        if "02" in icon_code: return u"\u26C5" # Sun behind cloud
        if "03" in icon_code or "04" in icon_code: return u"\u2601" # Cloud
        if "09" in icon_code or "10" in icon_code: return u"\u2614" # Rain
        if "11" in icon_code: return u"\u26C8" # Thunderstorm
        if "13" in icon_code: return u"\u2744" # Snow
        if "50" in icon_code: return u"\U0001F32B" # Fog/Mist
        return u"\U0001F300" # Cyclone (generic)

    def _create_group_frame(self, title):
        """Helper to create a themed QFrame for grouping sensors."""
        frame = QFrame(self)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setFrameShadow(QFrame.Raised)
        
        # Assign a unique object name for weather frame to find it later
        if title == "Current Weather":
            frame.setObjectName("weatherFrame") 
        else:
            frame.setObjectName("groupFrame") # For QSS styling
            
        layout = QVBoxLayout(frame) # This implicitly sets layout on 'frame'
        title_label = QLabel(title)
        title_label.setFont(QFont("Inter", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("groupFrameTitle") # Unique name for group titles
        layout.addWidget(title_label)
        
        return frame, layout # Return both the frame and its layout

    def update_sensor_data(self, data):
        """
        Receives comprehensive sensor data and updates all relevant gauges and labels.
        This slot is connected to the SensorWorker's sensor_data_updated signal.
        """
        self.dht_temp_gauge.set_value(data.get("temperature", 0))
        self.dht_hum_gauge.set_value(data.get("humidity", 0))
        self.ultrasonic_gauge.set_value(data.get("ultrasonic", 0))
        self.sound_gauge.set_value(data.get("sound", 0))
        self.light_gauge.set_value(data.get("light", 0))
        self.rotary_angle_gauge.set_value(data.get("rotary_angle", 0))

        # Update button status
        button_state = data.get("button", 0)
        self.button_label.setText("Button: {}".format("ON" if button_state == 1 else "OFF"))

        # Relay and LED Bar status are updated via separate signals in main_window.py
        # because their state is controlled, not just read from sensor_data.
        # However, for initial display, we can set them if needed.
        # The sensor_manager already emits these signals, so we can connect to them
        # from main_window directly, or have the main_window pass the state here.
        # For simplicity, we'll rely on the main_window connecting to specific signals
        # from sensor_manager for relay/LED bar to keep this dashboard simple.

    def update_relay_status(self, state):
        """
        Updates the displayed status of the Relay.
        This slot is connected to the SensorManager's relay_status_changed signal.
        """
        self.relay_status_label.setText("Relay: {}".format("ON" if state == 1 else "OFF"))

    def update_led_bar_status(self, level):
        """
        Updates the displayed level of the LED Bar.
        This slot is connected to the SensorManager's led_bar_status_changed signal.
        """
        self.led_bar_dashboard_widget.set_lit_segments(level)


    def set_style(self):
        """Applies specific styling for the dashboard tab."""
        self.setStyleSheet("""
            QWidget#DashboardTab {
                background-color: transparent; /* Main window stylesheet will cover this */
            }
            /*
            QFrame#groupFrame, QFrame#weatherFrame {
                border: 1px solid #555;
                border-radius: 10px;
                background-color: rgba(40, 40, 40, 0.7);
                margin: 5px;
                padding: 10px;
            }
            QLabel#groupFrameTitle {
                color: #ADD8E6;
                padding-bottom: 5px;
            }
            QLabel {
                color: #EEE;
            }
            */
        """)

    def _set_theme_colors_for_gauges(self):
        """
        Explicitly calls _set_theme_colors on all GaugeWidget instances
        within this tab to update their internal color attributes.
        """
        self.dht_temp_gauge._set_theme_colors()
        self.dht_hum_gauge._set_theme_colors()
        self.ultrasonic_gauge._set_theme_colors()
        self.sound_gauge._set_theme_colors()
        self.light_gauge._set_theme_colors()
        self.rotary_angle_gauge._set_theme_colors()
        # Also ensure labels in the dashboard get their colors updated if not covered by QSS
        current_theme_palette = {
            "dark_theme": "#abb2bf",
            "light_theme": "#333333",
            "blue_theme": "#e0f2f7",
            "dark_gray_theme": "#fdfdfd",
            "forest_green_theme": "#FFFFFF",
            "warm_sepia_theme": "#F5DEB3",
            "ocean_blue_theme": "#E0FFFF",
            "vibrant_purple_theme": "#E6E6FA",
            "light_modern_theme": "#333333",
            "high_contrast_theme": "#FFFF00"
        }
        text_color = current_theme_palette.get(self.config.get_setting("current_theme", "dark_theme"))
        if text_color:
            self.button_label.setStyleSheet("color: {};".format(text_color))
            self.relay_status_label.setStyleSheet("color: {};".format(text_color))
            self.weather_temp_label.setStyleSheet("color: {};".format(text_color))
            self.weather_desc_label.setStyleSheet("color: {};".format(text_color))
            self.weather_details_label.setStyleSheet("color: {};".format(text_color))
            # Update the title labels for group frames
            for label in self.findChildren(QLabel, "groupFrameTitle"):
                label.setStyleSheet("color: {};".format(current_theme_palette.get(self.config.get_setting('current_theme', 'dark_theme'))))

