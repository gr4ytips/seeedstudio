# ui/weather_tab.py
import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTabWidget, QHBoxLayout, QScrollArea, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QColor # Import QColor
from datetime import datetime # Ensure datetime is explicitly imported here

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.logger import Logger
from utils.weather_api import WeatherAPI
from utils.config_manager import ConfigManager

class WeatherTab(QWidget):
    """
    Separate tab to display detailed weather forecast (current, 24-hour, 5-day).
    """
    def __init__(self, parent=None):
        super(WeatherTab, self).__init__(parent)
        self.logger = Logger.get_logger()
        self.config = ConfigManager.get_instance()
        self.weather_api = WeatherAPI()

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        
        self._setup_ui()
        self._set_theme_colors() # Set initial theme colors for dynamic elements
        self.set_style() # Apply QSS for static elements
        self.logger.info("WeatherTab initialized.")

    def _set_theme_colors(self):
        """Sets internal color attributes based on the current theme for dynamic elements."""
        current_theme = self.config.get_setting("current_theme", "dark_theme")

        # Define color palettes for various themes
        theme_palettes = {
            "dark_theme": {
                "normal_text": QColor("#abb2bf"), # Light gray
                "warning_text": QColor("#FF4500"), # OrangeRed
                "success_text": QColor("#7CFC00"), # LimeGreen (not used directly, but good to have)
                "frame_background": QColor(30, 30, 30, 0.7),
                "frame_border": QColor(102, 102, 102), # #666
                "card_background": QColor(50, 50, 50, 0.8),
                "card_border": QColor(68, 68, 68), # #444
            },
            "light_theme": {
                "normal_text": QColor("#333333"),
                "warning_text": QColor("#FF4500"),
                "success_text": QColor("#28A745"),
                "frame_background": QColor(255, 255, 255, 0.9),
                "frame_border": QColor(204, 204, 204), # #CCC
                "card_background": QColor(248, 248, 248, 0.95),
                "card_border": QColor(220, 220, 220), # #DDD
            },
            "blue_theme": {
                "normal_text": QColor("#e0f2f7"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#3CB371"),
                "frame_background": QColor(26, 42, 64, 0.7),
                "frame_border": QColor(60, 101, 149),
                "card_background": QColor(43, 74, 104, 0.8),
                "card_border": QColor(36, 68, 97),
            },
            "dark_gray_theme": {
                "normal_text": QColor("#fdfdfd"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#3CB371"),
                "frame_background": QColor(40, 40, 40, 0.7),
                "frame_border": QColor(90, 90, 90),
                "card_background": QColor(60, 60, 60, 0.8),
                "card_border": QColor(80, 80, 80),
            },
            "forest_green_theme": {
                "normal_text": QColor("#FFFFFF"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#9ACD32"),
                "frame_background": QColor(30, 80, 30, 0.7),
                "frame_border": QColor(60, 120, 60),
                "card_background": QColor(50, 100, 50, 0.8),
                "card_border": QColor(40, 90, 40),
            },
            "warm_sepia_theme": {
                "normal_text": QColor("#F5DEB3"),
                "warning_text": QColor("#CD5C5C"),
                "success_text": QColor("#6B8E23"),
                "frame_background": QColor(80, 50, 30, 0.7),
                "frame_border": QColor(120, 90, 60),
                "card_background": QColor(100, 70, 40, 0.8),
                "card_border": QColor(90, 60, 30),
            },
            "ocean_blue_theme": {
                "normal_text": QColor("#E0FFFF"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#66CDAA"),
                "frame_background": QColor(30, 70, 120, 0.7),
                "frame_border": QColor(50, 100, 180),
                "card_background": QColor(40, 80, 130, 0.8),
                "card_border": QColor(30, 70, 120),
            },
            "vibrant_purple_theme": {
                "normal_text": QColor("#E6E6FA"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#7FFF00"),
                "frame_background": QColor(60, 20, 100, 0.7),
                "frame_border": QColor(100, 50, 150),
                "card_background": QColor(80, 40, 120, 0.8),
                "card_border": QColor(70, 30, 110),
            },
            "light_modern_theme": {
                "normal_text": QColor("#333333"),
                "warning_text": QColor("#FF4500"),
                "success_text": QColor("#28A745"),
                "frame_background": QColor(255, 255, 255, 0.9),
                "frame_border": QColor(160, 160, 160), # #A0A0A0
                "card_background": QColor(248, 248, 248, 0.95),
                "card_border": QColor(220, 220, 220),
            },
            "high_contrast_theme": {
                "normal_text": QColor("#FFFF00"), # Yellow
                "warning_text": QColor("#FF0000"), # Red
                "success_text": QColor("#00FF00"), # Green
                "frame_background": QColor(0, 0, 0, 0.9),
                "frame_border": QColor(0, 255, 255), # Cyan
                "card_background": QColor(17, 17, 17, 0.95),
                "card_border": QColor(255, 0, 255), # Magenta
            }
        }

        palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"]) # Fallback to dark
        
        self.normal_text_color = palette["normal_text"]
        self.warning_text_color = palette["warning_text"]
        self.frame_background_color = palette["frame_background"] # New: for main frames
        self.frame_border_color = palette["frame_border"]         # New: for main frames
        self.card_background_color = palette["card_background"]   # New: for forecast cards
        self.card_border_color = palette["card_border"]           # New: for forecast cards
        
        # Update current weather labels text color
        if hasattr(self, 'current_temp_label'): # Check if widgets are already created
            self.current_temp_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
            self.current_desc_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
            self.current_details_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
            self.current_icon_label.setStyleSheet("color: {};".format(self.normal_text_color.name())) # For emoji fallback

    def _setup_ui(self):
        """Sets up the UI elements for the weather tab."""
        title_label = QLabel("Weather Forecast")
        title_label.setFont(QFont("Inter", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setContentsMargins(0, 20, 0, 20)
        self.main_layout.addWidget(title_label)

        self.tab_widget = QTabWidget()
        self.tab_widget.setDocumentMode(True)
        self.tab_widget.setTabsClosable(False)
        self.tab_widget.setMovable(True)
        self.tab_widget.tabBar().setFont(QFont("Inter", 10))

        # Current Weather Tab
        self.current_weather_page = QWidget()
        self.current_weather_layout = QVBoxLayout(self.current_weather_page)
        self.current_weather_layout.setAlignment(Qt.AlignCenter)
        self._add_current_weather_widgets(self.current_weather_layout)
        self.tab_widget.addTab(self.current_weather_page, "Current Weather")

        # 24-Hour Forecast Tab
        self.hourly_forecast_page = QScrollArea()
        self.hourly_forecast_page.setWidgetResizable(True)
        hourly_content_widget = QWidget()
        self.hourly_forecast_layout = QHBoxLayout(hourly_content_widget) # Horizontal for hourly blocks
        self.hourly_forecast_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.hourly_forecast_page.setWidget(hourly_content_widget)
        self.tab_widget.addTab(self.hourly_forecast_page, "24-Hour Forecast")

        # 5-Day Forecast Tab - Changed to QHBoxLayout
        self.daily_forecast_page = QScrollArea()
        self.daily_forecast_page.setWidgetResizable(True)
        daily_content_widget = QWidget()
        self.daily_forecast_layout = QHBoxLayout(daily_content_widget) # Changed to QHBoxLayout
        self.daily_forecast_layout.setAlignment(Qt.AlignLeft | Qt.AlignVCenter) # Align horizontally to left
        self.daily_forecast_page.setWidget(daily_content_widget)
        self.tab_widget.addTab(self.daily_forecast_page, "5-Day Forecast")

        self.main_layout.addWidget(self.tab_widget)
        self.main_layout.addStretch(1)

        self.weather_update_timer = QTimer(self)
        # --- MODIFICATION START ---
        # Connect to the public method
        self.weather_update_timer.timeout.connect(self.fetch_and_update_weather) 
        # --- MODIFICATION END ---
        # Update current weather more frequently, forecast less often
        self.weather_update_timer.start(self.config.get_setting("weather_update_interval_ms", 300000)) # 5 minutes
        # --- MODIFICATION START ---
        # Initial fetch using the public method
        self.fetch_and_update_weather()
        # --- MODIFICATION END ---

    def _add_current_weather_widgets(self, layout):
        """Adds widgets for current weather display."""
        current_frame = QFrame(self)
        current_frame.setFrameShape(QFrame.StyledPanel)
        current_frame.setFrameShadow(QFrame.Raised)
        current_frame.setObjectName("weatherFrame")
        current_frame.setMinimumSize(350, 250)
        current_frame.setMaximumSize(450, 350)

        current_layout = QVBoxLayout(current_frame)
        current_layout.setAlignment(Qt.AlignCenter)
        

        self.current_icon_label = QLabel()
        self.current_icon_label.setAlignment(Qt.AlignCenter)
        self.current_icon_label.setFixedSize(96, 96)

        self.current_temp_label = QLabel("Loading...")
        self.current_temp_label.setAlignment(Qt.AlignCenter)
        self.current_temp_label.setFont(QFont("Inter", 36, QFont.Bold))

        self.current_desc_label = QLabel("")
        self.current_desc_label.setAlignment(Qt.AlignCenter)
        self.current_desc_label.setFont(QFont("Inter", 18))

        self.current_details_label = QLabel("")
        self.current_details_label.setAlignment(Qt.AlignCenter)
        self.current_details_label.setFont(QFont("Inter", 12))

        current_layout.addWidget(self.current_icon_label)
        current_layout.addWidget(self.current_temp_label)
        current_layout.addWidget(self.current_desc_label)
        current_layout.addWidget(self.current_details_label)
        current_layout.addStretch(1)

        layout.addWidget(current_frame)

    def _create_forecast_card(self, time_str, icon_code, temp, desc, humidity, wind):
        """Helper to create a QFrame representing a single forecast entry."""
        card = QFrame()
        card.setFrameShape(QFrame.StyledPanel)
        card.setFrameShadow(QFrame.Raised)
        card.setObjectName("forecastCard")
        card.setFixedSize(160, 220) # Fixed size for uniform cards

        card_layout = QVBoxLayout(card)
        card_layout.setAlignment(Qt.AlignCenter)

        time_label = QLabel(time_str)
        time_label.setFont(QFont("Inter", 10, QFont.Bold))
        time_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(time_label)

        icon_label = QLabel()
        icon_label.setAlignment(Qt.AlignCenter)
        icon_label.setFixedSize(50, 50)
        # Use emoji fallback as in dashboard_tab
        icon_path = os.path.join(project_root, 'icons', 'weather', "{}.png".format(icon_code))
        if os.path.exists(icon_path):
             pixmap = QPixmap(icon_path).scaled(50, 50, Qt.KeepAspectRatio, Qt.SmoothTransformation)
             icon_label.setPixmap(pixmap)
        else:
             icon_label.setText(self._get_weather_emoji(icon_code))
             icon_label.setFont(QFont("Inter", 28))
        card_layout.addWidget(icon_label)

        temp_label = QLabel("{:.1f}°C".format(temp))
        temp_label.setFont(QFont("Inter", 16, QFont.Bold))
        temp_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(temp_label)

        desc_label = QLabel(desc)
        desc_label.setFont(QFont("Inter", 9))
        desc_label.setAlignment(Qt.AlignCenter)
        desc_label.setWordWrap(True)
        card_layout.addWidget(desc_label)

        details_label = QLabel("Hum: {}%\nWind: {:.1f}m/s".format(humidity, wind))
        details_label.setFont(QFont("Inter", 8))
        details_label.setAlignment(Qt.AlignCenter)
        card_layout.addWidget(details_label)
        
        card_layout.addStretch(1)

        # Apply styles immediately after creating labels within the card
        # This will ensure the initial color is correct based on the current theme
        # Also apply card background and border here if not handled by set_style() dynamically
        card.setStyleSheet("""
            QFrame#forecastCard {{
                border: 1px solid {card_border_color};
                border-radius: 8px;
                background-color: {card_background_color};
                margin: 5px;
                padding: 8px;
            }}
            QLabel {{
                color: {normal_text_color};
            }}
        """.format(
            card_border_color=self.card_border_color.name(),
            card_background_color=self.card_background_color.name(),
            normal_text_color=self.normal_text_color.name()
        ))

        return card

    def _update_forecast_card_styles(self):
        """Updates the stylesheet of all labels within existing forecast cards."""
        # Update hourly forecast cards
        for i in range(self.hourly_forecast_layout.count()):
            item = self.hourly_forecast_layout.itemAt(i)
            # Ensure the item is a widget and not a stretch
            if item and item.widget() and item.widget().objectName() == "forecastCard":
                card = item.widget()
                card.setStyleSheet("""
                    QFrame#forecastCard {{
                        border: 1px solid {card_border_color};
                        border-radius: 8px;
                        background-color: {card_background_color};
                        margin: 5px;
                        padding: 8px;
                    }}
                    QLabel {{
                        color: {normal_text_color};
                    }}
                """.format(
                    card_border_color=self.card_border_color.name(),
                    card_background_color=self.card_background_color.name(),
                    normal_text_color=self.normal_text_color.name()
                ))

        # Update daily forecast cards
        for i in range(self.daily_forecast_layout.count()):
            item = self.daily_forecast_layout.itemAt(i)
            # Ensure the item is a widget and not a stretch
            if item and item.widget() and item.widget().objectName() == "forecastCard":
                card = item.widget()
                card.setStyleSheet("""
                    QFrame#forecastCard {{
                        border: 1px solid {card_border_color};
                        border-radius: 8px;
                        background-color: {card_background_color};
                        margin: 5px;
                        padding: 8px;
                    }}
                    QLabel {{
                        color: {normal_text_color};
                    }}
                """.format(
                    card_border_color=self.card_border_color.name(),
                    card_background_color=self.card_background_color.name(),
                    normal_text_color=self.normal_text_color.name()
                ))


    def _get_weather_emoji(self, icon_code):
        """Maps OpenWeatherMap icon codes to simple emojis."""
        if "01" in icon_code: return u"\u2600" # Sun
        if "02" in icon_code: return u"\u26C5" # Sun behind cloud
        if "03" in icon_code or "04" in icon_code: return u"\u2601" # Cloud
        if "09" in icon_code or "10" in icon_code: return u"\u2614" # Rain
        if "11" in icon_code: return u"\u26C8" # Thunderstorm
        if "13" in icon_code: return u"\u2744" # Snow
        if "50" in icon_code: return u"\U0001F32B" # Fog/Mist
        return u"\U0001F300" # Cyclone (generic)


    # --- MODIFICATION START ---
    # Renamed from _fetch_and_update_all_weather to fetch_and_update_weather
    def fetch_and_update_weather(self):
    # --- MODIFICATION END ---
        """Fetches all weather data (current, 24-hr, 5-day) and updates UI."""
        self.logger.info("Fetching all weather data...")
        city = self.config.get_setting("weather_city", "Frisco")
        country = self.config.get_setting("weather_country_code", "US")

        # Re-apply theme colors just in case theme changed
        self._set_theme_colors()

        # Update Current Weather
        current_weather = self.weather_api.get_current_weather(city, country)
        if current_weather:
            temp = current_weather["temperature"]
            desc = current_weather["description"].capitalize()
            humidity = current_weather["humidity"]
            wind_speed = current_weather["wind_speed"]
            icon_code = current_weather["icon"]
            
            self.current_temp_label.setText("{:.1f}°C".format(temp))
            self.current_desc_label.setText(desc)
            self.current_details_label.setText("Humidity: {}%\nWind: {:.1f} m/s\nCity: {}".format(humidity, wind_speed, current_weather["city_name"]))
            
            icon_path = os.path.join(project_root, 'icons', 'weather', "{}.png".format(icon_code))
            if os.path.exists(icon_path):
                 pixmap = QPixmap(icon_path).scaled(96, 96, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                 self.current_icon_label.setPixmap(pixmap)
            else:
                 self.current_icon_label.setText(self._get_weather_emoji(icon_code))
                 self.current_icon_label.setFont(QFont("Inter", 56))
            self.current_icon_label.setToolTip(desc)
            # Ensure current weather labels are also updated here
            self.current_temp_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
            self.current_desc_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
            self.current_details_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
            self.current_icon_label.setStyleSheet("color: {};".format(self.normal_text_color.name()))
        else:
            self.current_temp_label.setText("N/A")
            self.current_desc_label.setText("Error")
            self.current_details_label.setText("Check API Key/Connection")
            self.current_icon_label.setText("?")
            self.current_icon_label.setFont(QFont("Inter", 56))
            self.current_temp_label.setStyleSheet("color: {};".format(self.warning_text_color.name()))
            self.current_desc_label.setStyleSheet("color: {};".format(self.warning_text_color.name()))
            self.current_details_label.setStyleSheet("color: {};".format(self.warning_text_color.name()))
            self.current_icon_label.setStyleSheet("color: {};".format(self.warning_text_color.name()))


        # Update Forecasts
        forecasts = self.weather_api.get_forecast(city, country)
        if forecasts:
            # Clear previous forecast cards from hourly layout
            for i in reversed(range(self.hourly_forecast_layout.count())):
                item = self.hourly_forecast_layout.itemAt(i)
                if item is not None and item.widget() is not None:
                    widget_to_remove = item.widget()
                    self.hourly_forecast_layout.removeWidget(widget_to_remove)
                    widget_to_remove.setParent(None)
            
            # Clear previous forecast cards from daily layout
            for i in reversed(range(self.daily_forecast_layout.count())):
                item = self.daily_forecast_layout.itemAt(i)
                if item is not None and item.widget() is not None:
                    widget_to_remove = item.widget()
                    self.daily_forecast_layout.removeWidget(widget_to_remove)
                    widget_to_remove.setParent(None)

            # Populate 24-Hour Forecast (next 8 entries = 24 hours at 3-hour intervals)
            for i, fc in enumerate(forecasts[:8]):
                dt_obj = datetime.strptime(fc["dt_txt"], "%Y-%m-%d %H:%M:%S")
                time_str = dt_obj.strftime("%H:%M\n%b %d")
                card = self._create_forecast_card(
                    time_str, fc["icon"], fc["temperature"], fc["description"].capitalize(),
                    fc["humidity"], fc["wind_speed"]
                )
                self.hourly_forecast_layout.addWidget(card)
            self.hourly_forecast_layout.addStretch(1) # Push cards to left

            # Populate 5-Day Forecast (one entry per day, e.g., closest to noon)
            daily_forecasts = {}
            for fc in forecasts:
                date = fc["dt_txt"].split(" ")[0]
                hour = int(fc["dt_txt"].split(" ")[1].split(":")[0])
                # Prioritize a mid-day forecast for each day if not already added
                if date not in daily_forecasts or (hour >= 12 and hour <= 15 and daily_forecasts[date]["hour"] not in range(12,16)):
                    daily_forecasts[date] = {"forecast": fc, "hour": hour}
            
            # Sort by date and take the first 5 unique days
            sorted_daily_dates = sorted(daily_forecasts.keys())
            for date_key in sorted_daily_dates[:5]:
                fc = daily_forecasts[date_key]["forecast"] # Corrected variable name here
                dt_obj = datetime.strptime(fc["dt_txt"], "%Y-%m-%d %H:%M:%S")
                day_str = dt_obj.strftime("%A, %b %d")
                card = self._create_forecast_card(
                    day_str, fc["icon"], fc["temperature"], fc["description"].capitalize(),
                    fc["humidity"], fc["wind_speed"]
                )
                self.daily_forecast_layout.addWidget(card)
            self.daily_forecast_layout.addStretch(1) # Push cards to left for horizontal layout

            # After creating/updating cards, apply styles
            self._update_forecast_card_styles()
        else:
            # Clear previous forecast cards if an error occurred
            for i in reversed(range(self.hourly_forecast_layout.count())):
                item = self.hourly_forecast_layout.itemAt(i)
                if item is not None and item.widget() is not None:
                    widget_to_remove = item.widget()
                    self.hourly_forecast_layout.removeWidget(widget_to_remove)
                    widget_to_remove.setParent(None)
            
            for i in reversed(range(self.daily_forecast_layout.count())):
                item = self.daily_forecast_layout.itemAt(i)
                if item is not None and item.widget() is not None:
                    widget_to_remove = item.widget()
                    self.daily_forecast_layout.removeWidget(widget_to_remove)
                    widget_to_remove.setParent(None)
            
            # Display error messages for forecast tabs
            error_label_hourly = QLabel("Failed to load 24-hour forecast. Check API Key/Connection.")
            error_label_hourly.setStyleSheet("color: {};".format(self.warning_text_color.name()))
            self.hourly_forecast_layout.addWidget(error_label_hourly)
            self.hourly_forecast_layout.addStretch(1) # Push error message to left
            
            error_label_daily = QLabel("Failed to load 5-day forecast. Check API Key/Connection.")
            error_label_daily.setStyleSheet("color: {};".format(self.warning_text_color.name()))
            self.daily_forecast_layout.addWidget(error_label_daily)
            self.daily_forecast_layout.addStretch(1) # Push error message to left


    def set_style(self):
        """Applies specific styling for the tab."""
        self.setStyleSheet("""
            QWidget#WeatherTab {{
                background-color: transparent;
            }}
            QLabel {{
                color: #EEE; /* Default text color */
            }}
            QLabel:hover {{
                color: #FFD700;
            }}
            QTabWidget::pane {{
                border: 1px solid {frame_border_color};
                background: {frame_background_color};
                border-radius: 10px;
            }}
            QTabWidget::tab-bar {{
                left: 5px;
            }}
            QTabBar::tab {{
                background: #555;
                color: white;
                border: 1px solid #777;
                border-bottom-color: #555;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 15px;
                min-width: 100px;
            }}
            QTabBar::tab:selected {{
                background: #1E90FF;
                border-color: #1E90FF;
                border-bottom-color: #1E90FF;
            }}
            QTabBar::tab:hover {{
                background: #777;
            }}
            QFrame#weatherFrame {{
                border: 1px solid {frame_border_color};
                border-radius: 15px;
                background-color: {frame_background_color};
                padding: 20px;
            }}
            /* QFrame#forecastCard styling is now handled directly in _create_forecast_card and _update_forecast_card_styles */
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollArea > QWidget > QWidget {{
                background-color: transparent;
            }}
        """.format(
            frame_border_color=self.frame_border_color.name(),
            frame_background_color=self.frame_background_color.name()
        ))

