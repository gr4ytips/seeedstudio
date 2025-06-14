from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt5.QtGui import QFont, QColor, QPainter, QPen, QBrush, QConicalGradient
from PyQt5.QtCore import Qt, QRectF, QSize, QPointF

import math

class DashboardGaugeWidget(QWidget):
    """
    A custom PyQt5 widget designed for the dashboard to display a sensor value
    in a compact, graphical gauge format. It shows the sensor name, current value,
    and unit, with a circular progress indicator and colors indicating alert levels.
    """
    def __init__(self, title, min_val, max_val, unit="", sensor_thresholds=None, parent=None):
        """
        Initializes the DashboardGaugeWidget.

        :param title: The title/name of the sensor (e.g., "Temperature").
        :param min_val: The minimum value for the sensor's scale.
        :param max_val: The maximum value for the sensor's scale.
        :param unit: The unit of measurement (e.g., "°C", "%", "cm").
        :param sensor_thresholds: A dictionary containing specific thresholds for this sensor
                                  (e.g., {"WARNING_HIGH": val, "CRITICAL_HIGH": val, ...}).
                                  If None, a default 'NORMAL' state is assumed.
        :param parent: The parent widget, if any.
        """
        super().__init__(parent)
        self.title = title
        self.min_val = float(min_val) # Ensure min_val is float for calculations
        self.max_val = float(max_val) # Ensure max_val is float for calculations
        self.unit = unit
        self.sensor_thresholds = sensor_thresholds if sensor_thresholds is not None else {}
        self._value = float('nan') # Current value, initialized to Not-a-Number
        self._alert_level = "NORMAL" # Current alert level

        # Default colors (will be overridden by set_theme_colors)
        self._bg_color = QColor("#3A3A3A")
        self._border_color = QColor("#5A5A5A")
        self._text_color = QColor("#E0E0E0")
        self._accent_color = QColor("#66BB6A") # Default accent for normal range/fill
        self._critical_color = QColor("red")
        self._warning_color = QColor("orange")
        self._normal_color = QColor("#66BB6A") # Default for normal range
        self._subtle_text_color = QColor("#B0B0B0") # For unit and title
        self._gauge_fill_color = QColor("#4A4A4A") # For the background fill of the gauge arc

        # Fonts
        self._title_font = QFont("Arial", 9)
        self._value_font = QFont("Arial", 16, QFont.Bold)
        self._unit_font = QFont("Arial", 8)

        self.setMinimumSize(120, 120) # Smaller size for dashboard
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


    def set_value(self, value):
        """
        Sets the current value of the gauge and updates its appearance.
        Also determines the alert level based on thresholds.

        :param value: The new sensor value.
        """
        old_alert_level = self._alert_level
        self._value = value
        self._alert_level = self._get_alert_level(value)
        if self._alert_level != old_alert_level:
            self.update() # Only repaint if alert level changes, or the value itself changes
        self.update() # Trigger a repaint

    def set_theme_colors(self, bg_color: str, border_color: str, text_color: str,
                         accent_color: str, critical_color: str, warning_color: str,
                         normal_color: str, subtle_text_color: str, gauge_fill_color: str):
        """
        Sets the theme-specific colors for the gauge.

        :param bg_color: Background color of the widget.
        :param border_color: Border color.
        :param text_color: General text color (for value).
        :param accent_color: Accent color, often used for normal state or highlights.
        :param critical_color: Color for critical alerts.
        :param warning_color: Color for warning alerts.
        :param normal_color: Color for normal state.
        :param subtle_text_color: Color for title and unit text.
        :param gauge_fill_color: Color for the inner fill of the gauge arc.
        """
        self._bg_color = QColor(bg_color)
        self._border_color = QColor(border_color)
        self._text_color = QColor(text_color)
        self._accent_color = QColor(accent_color)
        self._critical_color = QColor(critical_color)
        self._warning_color = QColor(warning_color)
        self._normal_color = QColor(normal_color)
        self._subtle_text_color = QColor(subtle_text_color)
        self._gauge_fill_color = QColor(gauge_fill_color)
        self.update() # Trigger repaint


    def _get_alert_level(self, value):
        """
        Determines the alert level based on the sensor value and predefined thresholds.
        """
        if math.isnan(value):
            return "UNKNOWN"

        if "CRITICAL_HIGH" in self.sensor_thresholds and value >= self.sensor_thresholds["CRITICAL_HIGH"]:
            return "CRITICAL_HIGH"
        if "WARNING_HIGH" in self.sensor_thresholds and value >= self.sensor_thresholds["WARNING_HIGH"]:
            return "WARNING_HIGH"
        if "CRITICAL_LOW" in self.sensor_thresholds and value <= self.sensor_thresholds["CRITICAL_LOW"]:
            return "CRITICAL_LOW"
        if "WARNING_LOW" in self.sensor_thresholds and value <= self.sensor_thresholds["WARNING_LOW"]:
            return "WARNING_LOW"
        
        return "NORMAL"

    def paintEvent(self, event):
        """
        Handles the painting of the DashboardGaugeWidget.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        side = min(self.width(), self.height())
        # Scale everything to a 120x120 logical space for dashboard
        painter.scale(side / 120.0, side / 120.0)
        
        # Draw background and border for the widget itself
        painter.setBrush(QBrush(self._bg_color))
        painter.setPen(QPen(self._border_color, 1)) # Thinner border for dashboard gauges
        painter.drawRoundedRect(0, 0, 120, 120, 8, 8) # Rounded corners


        # Define common parameters for the gauge arc
        arc_width = 10 # Width of the arc
        center_x, center_y = 60, 60 # Center of the logical 120x120 space
        radius = 50 # Radius of the gauge circle
        
        # Adjust rectangle for the arc
        arc_rect = QRectF(center_x - radius, center_y - radius, radius * 2, radius * 2)

        start_angle = 150 # Start from 7 o'clock
        end_angle = -120 # End at 5 o'clock (total 270 degrees clockwise)
        span_angle = (end_angle - start_angle) % 360 # Calculate span correctly

        # 1. Draw the background arc (the full range of the gauge)
        painter.setPen(QPen(self._gauge_fill_color, arc_width, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(arc_rect, start_angle * 16, span_angle * 16) # Qt angles are 1/16th of a degree


        # 2. Draw the value arc (colored based on alert level)
        value_normalized = (self._value - self.min_val) / (self.max_val - self.min_val)
        if math.isnan(value_normalized):
            value_normalized = 0 # If NaN, show empty arc
        
        # Clamp value between 0 and 1
        value_normalized = max(0.0, min(1.0, value_normalized))

        current_span = value_normalized * span_angle
        
        # Determine the color based on alert level
        arc_color = self._normal_color
        if self._alert_level in ["CRITICAL_HIGH", "CRITICAL_LOW"]:
            arc_color = self._critical_color
        elif self._alert_level in ["WARNING_HIGH", "WARNING_LOW"]:
            arc_color = self._warning_color
        
        painter.setPen(QPen(arc_color, arc_width, Qt.SolidLine, Qt.RoundCap))
        painter.drawArc(arc_rect, start_angle * 16, current_span * 16)

        # 3. Draw the inner circle fill and border (optional for dashboard, but good for definition)
        inner_radius = radius - arc_width / 2 - 2 # Smaller inner circle
        painter.setBrush(QBrush(self._bg_color))
        painter.setPen(QPen(self._border_color, 1)) # Thin border
        painter.drawEllipse(QPointF(center_x, center_y), inner_radius, inner_radius)


        # 4. Draw the title (sensor name) - top part of the gauge
        painter.setFont(self._title_font)
        painter.setPen(self._subtle_text_color) # Themed subtle text color for title
        title_text_rect = QRectF(arc_rect.x(), arc_rect.y() - 10, arc_rect.width(), radius * 0.4)
        painter.drawText(title_text_rect, Qt.AlignHCenter | Qt.AlignTop, self.title)

        # 5. Draw the numerical value in the center
        painter.setFont(self._value_font)
        # Set value color based on alert level
        value_color = self._critical_color if self._alert_level in ["CRITICAL_HIGH", "CRITICAL_LOW"] else self._text_color
        painter.setPen(value_color)

        display_numerical_value = ""
        if not math.isnan(self._value):
            if isinstance(self._value, float) and self._value % 1 != 0:
                display_numerical_value = "{:.1f}".format(self._value)
            else:
                display_numerical_value = "{}".format(int(self._value))
        else:
            display_numerical_value = "N/A"
        
        value_text_rect = QRectF(arc_rect.x(), arc_rect.y() + radius * 0.2, arc_rect.width(), arc_rect.height() * 0.6)
        painter.drawText(value_text_rect, Qt.AlignCenter, display_numerical_value)


        # 6. Draw unit (if applicable), below the numerical value
        unit_to_display = self.unit
        if unit_to_display in ["Raw", "State"]: # Don't display unit if it's 'Raw' or 'State'
            unit_to_display = ""
        
        if unit_to_display:
            painter.setFont(self._unit_font)
            painter.setPen(self._subtle_text_color) # Themed subtle unit text color
            
            unit_text_rect = QRectF(arc_rect.x(), arc_rect.y() + radius * 1.0, arc_rect.width(), radius * 0.3)
            painter.drawText(unit_text_rect, Qt.AlignHCenter | Qt.AlignTop, unit_to_display)

        painter.end()

    def sizeHint(self):
        """
        Provides a recommended size for the widget.
        """
        return QSize(120, 120) # Recommend a 120x120 size for dashboard
