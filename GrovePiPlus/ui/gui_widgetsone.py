from PyQt5.QtWidgets import QWidget, QLabel, QSizePolicy
from PyQt5.QtGui import QFont, QColor, QPainter, QPen
from PyQt5.QtCore import Qt, QRect, QSize # Import QSize

import math # For math.isnan
from utils.config_manager import ConfigManager # Import ConfigManager for theme access

class GaugeWidgetOne(QWidget):
    """
    A custom PyQt5 widget designed to display a sensor value as a gauge.
    It shows a circular gauge with a value display in the center and a title.
    The outer ring changes color based on the value's proximity to defined thresholds.
    """
    def __init__(self, title, min_val, max_val, unit="", sensor_thresholds=None, config_manager=None, parent=None):
        """
        Initializes the GaugeWidgetOne.

        :param title: The title of the gauge (e.g., "Temperature").
        :param min_val: The minimum value for the gauge's scale.
        :param max_val: The maximum value for the gauge's scale.
        :param unit: The unit of measurement (e.g., "°C", "さんも").
        :param sensor_thresholds: A dictionary containing specific thresholds for this sensor
                                  (e.g., {"WARNING_HIGH": val, "CRITICAL_HIGH": val, ...}).
                                  If None, a default 'NORMAL' state is assumed.
        :param config_manager: Reference to the ConfigManager for theme settings.
        :param parent: The parent widget, if any.
        """
        super().__init__(parent)
        self.title = title
        self.min_val = float(min_val) # Ensure min_val is float for calculations
        self.max_val = float(max_val) # Ensure max_val is float for calculations
        self.unit = unit
        self.original_unit = unit # Store the original unit to decide title modification
        self._value = float('nan') # Initialize current value to NaN for "no data" state
        self._alert_level = "NORMAL" # Initialize alert level

        # Store the actual sensor-specific thresholds
        self.sensor_thresholds = sensor_thresholds if sensor_thresholds is not None else {}

        self.config = config_manager if config_manager else ConfigManager.get_instance() # Get config instance
        self._set_theme_colors_internal() # Set initial theme colors based on current config

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Changed to Expanding for full responsiveness

    def _set_theme_colors_internal(self):
        """
        Sets internal color attributes based on the current theme from ConfigManager.
        This method is called internally or when the theme changes.
        """
        current_theme = self.config.get_setting("current_theme", "dark_theme")
        theme_palettes = {
            "dark_theme": {
                "background_color": QColor("#3A3A3A"), # Dark gray for the main filled background circle
                "border_color": QColor("#5A5A5A"),   # Slightly lighter gray for the main track border
                "text_color": QColor("#E0E0E0"),    # Off-white text for value and title
                "fill_color": QColor("#5A5A5A"),    # Light gray for the default fill (unfilled track)
                "accent_color": QColor("#66BB6A"),  # Green for the active filled part
                "critical_color": QColor("red"),    # Red
                "warning_color": QColor("orange"),  # Amber (Orange)
                "normal_color": QColor("#00BFFF")   # Vibrant Blue (though accent_color is primarily used for normal)
            },
            "light_theme": {
                "background_color": QColor("#F0F0F0"),
                "border_color": QColor("#C0C0C0"),
                "text_color": QColor("#333333"),
                "fill_color": QColor("#E0E0E0"),
                "accent_color": QColor("#40A750"),
                "critical_color": QColor("#CC0000"),
                "warning_color": QColor("#E5A000"),
                "normal_color": QColor("#007bff")
            },
            "blue_theme": {
                "background_color": QColor("#264264"),
                "border_color": QColor("#3c6595"),
                "text_color": QColor("#e0f2f7"),
                "fill_color": QColor("#2B4A68"),
                "accent_color": QColor("#4682B4"),
                "critical_color": QColor("#E74C3C"),
                "warning_color": QColor("#F39C12"),
                "normal_color": QColor("#4682B4")
            },
            "dark_gray_theme": {
                "background_color": QColor("#4B4F52"),
                "border_color": QColor("#6C7072"),
                "text_color": QColor("#fdfdfd"),
                "fill_color": QColor("#4a4d4f"),
                "accent_color": QColor("#6a737d"),
                "critical_color": QColor("#E74C3C"),
                "warning_color": QColor("#F39C12"),
                "normal_color": QColor("#6a737d")
            },
            "forest_green_theme": {
                "background_color": QColor("#2E7D32"),
                "border_color": QColor("#4CAF50"),
                "text_color": QColor("#FFFFFF"),
                "fill_color": QColor("#388E3C"),
                "accent_color": QColor("#66BB6A"),
                "critical_color": QColor("#E74C3C"),
                "warning_color": QColor("#F39C12"),
                "normal_color": QColor("#66BB6A")
            },
            "warm_sepia_theme": {
                "background_color": QColor("#5A2D0C"),
                "border_color": QColor("#A0522D"),
                "text_color": QColor("#F5DEB3"),
                "fill_color": QColor("#6C3817"),
                "accent_color": QColor("#A0522D"),
                "critical_color": QColor("#D35400"),
                "warning_color": QColor("#F39C12"),
                "normal_color": QColor("#A0522D")
            },
            "ocean_blue_theme": {
                "background_color": QColor("#002244"),
                "border_color": QColor("#005099"),
                "text_color": QColor("#E0FFFF"),
                "fill_color": QColor("#004488"),
                "accent_color": QColor("#4682B4"),
                "critical_color": QColor("#E74C3C"),
                "warning_color": QColor("#F39C12"),
                "normal_color": QColor("#4682B4")
            },
            "vibrant_purple_theme": {
                "background_color": QColor("#300050"),
                "border_color": QColor("#8A2BE2"),
                "text_color": QColor("#E6E6FA"),
                "fill_color": QColor("#5A1F8D"),
                "accent_color": QColor("#8A2BE2"),
                "critical_color": QColor("#E74C3C"),
                "warning_color": QColor("#F39C12"),
                "normal_color": QColor("#8A2BE2")
            },
            "light_modern_theme": {
                "background_color": QColor("#F8F8F8"),
                "border_color": QColor("#C0C0C0"),
                "text_color": QColor("#333333"),
                "fill_color": QColor("#D0D0D0"),
                "accent_color": QColor("#607D8B"),
                "critical_color": QColor("#CC0000"),
                "warning_color": QColor("#E5A000"),
                "normal_color": QColor("#607D8B")
            },
            "high_contrast_theme": {
                "background_color": QColor("#111111"),
                "border_color": QColor("#FF00FF"),
                "text_color": QColor("#FFFF00"),
                "fill_color": QColor("#333333"),
                "accent_color": QColor("#00FF00"),
                "critical_color": QColor("#FF0000"),
                "warning_color": QColor("#FFA500"),
                "normal_color": QColor("#00FF00")
            }
        }
        palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"])

        self.background_color = palette["background_color"]
        self.border_color = palette["border_color"]
        self.text_color = palette["text_color"]
        self.fill_color = palette["fill_color"] # This is the color for the unfilled part of the track
        self.accent_color = palette["accent_color"] # This is the color for the filled part of the track
        
        # Override threshold colors to use theme colors if provided
        self.threshold_colors = {
            "CRITICAL_HIGH": palette["critical_color"],
            "CRITICAL_LOW": palette["critical_color"],
            "WARNING_HIGH": palette["warning_color"],
            "WARNING_LOW": palette["warning_color"],
            "NORMAL": palette["accent_color"] # For GaugeWidgetOne, "NORMAL" uses accent_color for the fill
        }
        self.update() # Trigger repaint


    def set_theme_colors(self, bg_color: str, border_color: str, text_color: str,
                         accent_color: str, critical_color: str, warning_color: str,
                         normal_color: str, gauge_fill_color: str):
        """
        Public method to set the theme-specific colors for the gauge widget from external calls.
        This allows external components like tabs to update the gauge's colors.
        """
        self.background_color = QColor(bg_color)
        self.border_color = QColor(border_color)
        self.text_color = QColor(text_color)
        self.fill_color = QColor(gauge_fill_color) # Corresponds to the unfilled part of the track
        self.accent_color = QColor(accent_color) # Corresponds to the filled part of the track
        
        # Explicitly set alert colors based on the passed parameters
        self.threshold_colors["CRITICAL_HIGH"] = QColor(critical_color)
        self.threshold_colors["CRITICAL_LOW"] = QColor(critical_color)
        self.threshold_colors["WARNING_HIGH"] = QColor(warning_color)
        self.threshold_colors["WARNING_LOW"] = QColor(warning_color)
        self.threshold_colors["NORMAL"] = QColor(normal_color) # Use normal_color passed in

        self.update() # Trigger repaint


    def set_value(self, value):
        """
        Sets the current value for the gauge and updates its alert level.

        :param value: The new sensor value.
        """
        if value is not None and not math.isnan(value):
            self._value = value
            self._update_alert_level() # Update alert level based on new value
        else:
            self._value = float('nan') # Use NaN to indicate no valid data
            self._alert_level = "NORMAL" # Reset to normal if no data
        self.update() # Trigger a repaint of the widget

    def _update_alert_level(self):
        """
        Determines the current alert level based on the sensor's actual thresholds.
        """
        if math.isnan(self._value):
            self._alert_level = "NORMAL" # Default to normal if no valid data
            return

        current_value = self._value
        thresholds = self.sensor_thresholds

        # Check CRITICAL_HIGH
        if "CRITICAL_HIGH" in thresholds and current_value >= thresholds["CRITICAL_HIGH"]["value"]:
            self._alert_level = "CRITICAL_HIGH"
        # Check WARNING_HIGH (only if not already critical high)
        elif "WARNING_HIGH" in thresholds and current_value >= thresholds["WARNING_HIGH"]["value"]:
            self._alert_level = "WARNING_HIGH"
        # Check CRITICAL_LOW (only if not already high alerts)
        elif "CRITICAL_LOW" in thresholds and current_value <= thresholds["CRITICAL_LOW"]["value"]:
            self._alert_level = "CRITICAL_LOW"
        # Check WARNING_LOW (only if not already low/high alerts)
        elif "WARNING_LOW" in thresholds and current_value <= thresholds["WARNING_LOW"]["value"]:
            self._alert_level = "WARNING_LOW"
        else:
            self._alert_level = "NORMAL" # Value is within normal operating range


    def paintEvent(self, event):
        """
        Paints the gauge widget, including the background arc, active value arc,
        center circle, current value text, and title text. The active arc's
        color is determined by the current alert level.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        side = min(rect.width(), rect.height()) # Get the smaller side to keep it square

        # Scale the painter to a virtual 200x200 canvas.
        # This allows all drawing coordinates to be defined relative to a 200x200 square,
        # and they will automatically scale to the actual widget size.
        painter.translate(rect.center())
        painter.scale(side / 200.0, side / 200.0)
        painter.translate(-100, -100) # Translate back so (0,0) is top-left of virtual 200x200 canvas

        # Define the bounding rectangle for the arc
        arc_rect = QRectF(10, 10, 180, 180) # Virtual 200x200 canvas, centered 180x180 arc

        # Draw the background track (unfilled part)
        painter.setPen(QPen(self.fill_color, 12, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(arc_rect, 135 * 16, -270 * 16) # Arc from 135 to -135 (270 degrees total)

        # Draw the filled arc based on the current value
        if not math.isnan(self._value):
            angle_range = 270 # Total degrees for the gauge
            value_range = self.max_val - self.min_val
            
            # Calculate the angle based on the current value
            # Ensure value is within bounds for correct angle calculation
            clamped_value = max(self.min_val, min(self.max_val, self._value))
            
            if value_range > 0:
                normalized_value = (clamped_value - self.min_val) / value_range
                fill_angle = -int(normalized_value * angle_range) # Negative for counter-clockwise
            else:
                fill_angle = 0 # Avoid division by zero, no fill if range is 0

            # Get color based on alert level
            active_arc_color = self.threshold_colors.get(self._alert_level, self.accent_color)
            painter.setPen(QPen(active_arc_color, 12, Qt.SolidLine, Qt.RoundCap))
            painter.drawArc(arc_rect, 135 * 16, fill_angle * 16)

        # Draw the central circle (background for value text)
        painter.setBrush(self.background_color)
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(QRectF(50, 50, 100, 100)) # Center circle in virtual 200x200 canvas

        # Prepare font for value
        value_font = QFont("Arial", 20)
        value_font.setBold(True)
        painter.setFont(value_font)
        painter.setPen(self.text_color)

        # Define units that should be moved to the title
        units_to_move = ["Raw", "cm", "%", "°C", "°F"]

        # Modify display_value_text based on whether the original unit is in the list
        display_value_text = ""
        if math.isnan(self._value):
            if self.original_unit in units_to_move:
                display_value_text = "--"
            else:
                display_value_text = "--{0}".format(self.original_unit)
        else:
            if self.original_unit in units_to_move:
                display_value_text = "{:.1f}".format(self._value)
            else:
                display_value_text = "{:.1f}{0}".format(self._value, self.original_unit)

        # Draw the value text
        value_text_draw_rect = QRect(50, 50, 100, 100)
        painter.drawText(value_text_draw_rect, Qt.AlignCenter, display_value_text)

        # Draw the gauge title below the value
        title_font = QFont("Arial", 10)
        title_font.setBold(False)
        painter.setFont(title_font)
        painter.setPen(self.text_color)

        # Adjust title based on original unit, appending the unit in parentheses if applicable
        displayed_title = self.title
        if self.original_unit == "Raw":
            displayed_title = "{0} (Raw)".format(self.title)
        elif self.original_unit == "cm":
            displayed_title = "{0} (cm)".format(self.title)
        elif self.original_unit == "%":
            displayed_title = "{0} (%)".format(self.title)
        elif self.original_unit == "°C":
            displayed_title = "{0} (°C)".format(self.title)
        elif self.original_unit == "°F":
            displayed_title = "{0} (°F)".format(self.title)

        title_vertical_offset_from_bottom = 25
        title_y_pos = 200 - title_vertical_offset_from_bottom
        
        title_draw_rect = QRect(0, int(title_y_pos), 200, title_vertical_offset_from_bottom) # Full width (0-200)
        painter.drawText(title_draw_rect, Qt.AlignHCenter | Qt.AlignTop, displayed_title)

    def minimumSizeHint(self):
        """
        Provides a reasonable minimum size hint for the layout system.
        """
        return QSize(120, 120)

    def sizeHint(self):
        """
        Provides an ideal size hint for the layout system.
        """
        return QSize(200, 200)
