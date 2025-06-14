# ui/gauge_widget.py
import math # Import the math module for trigonometric functions
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF

from utils.config_manager import ConfigManager # Import ConfigManager for theme access

class GaugeWidget(QWidget):
    """
    A custom QWidget to display a value as a gauge.
    """
    def __init__(self, title, unit, min_val, max_val, config_manager=None, parent=None): # Added config_manager
        super(GaugeWidget, self).__init__(parent)
        self.title = title
        self.unit = unit
        self.min_val = min_val
        self.max_val = max_val
        self.current_value = min_val

        self.config = config_manager if config_manager else ConfigManager.get_instance() # Get config instance

        # Removed setMinimumSize and setMaximumSize here to allow full responsiveness
        # The parent layout (BasicAnalogSensorsTab) will now control the size more fluidly.

        self.layout = QVBoxLayout(self)
        self.value_label = QLabel("{:.1f} {}".format(self.current_value, self.unit))
        self.value_label.setAlignment(Qt.AlignCenter)
        # Font size for value label will be set dynamically in paintEvent
        
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        # Font size for title label will be set dynamically in paintEvent
        
        # Layout for labels - position them relative to the gauge
        # Add labels to the layout, the gauge drawing will be independent
        self.layout.addWidget(self.title_label, alignment=Qt.AlignTop | Qt.AlignCenter)
        self.layout.addStretch(1) # Push value label down
        self.layout.addWidget(self.value_label, alignment=Qt.AlignCenter)
        self.layout.addStretch(1) # Push value label up

        self.setToolTip(self.title)
        self._set_theme_colors() # Set initial theme colors

    def _set_theme_colors(self):
        """Sets internal color attributes based on the current theme."""
        current_theme = self.config.get_setting("current_theme", "dark_theme")

        # Define color palettes for each theme
        theme_palettes = {
            "dark_theme": {
                "background_arc": QColor(100, 100, 100),
                "tick_line": QColor(200, 200, 200),
                "center_circle": QColor(50, 50, 50),
                "text_color": QColor(171, 178, 191) # abb2bf for labels (light gray)
            },
            "light_theme": {
                "background_arc": QColor(200, 200, 200),
                "tick_line": QColor(80, 80, 80),
                "center_circle": QColor(150, 150, 150),
                "text_color": QColor(51, 51, 51)
            },
            "blue_theme": {
                "background_arc": QColor(50, 100, 150),
                "tick_line": QColor(224, 242, 247),
                "center_circle": QColor(26, 42, 64),
                "text_color": QColor(224, 242, 247)
            },
            "dark_gray_theme": {
                "background_arc": QColor(80, 80, 80),
                "tick_line": QColor(220, 220, 220),
                "center_circle": QColor(40, 40, 40),
                "text_color": QColor(240, 240, 240)
            },
            "forest_green_theme": {
                "background_arc": QColor(80, 150, 80),
                "tick_line": QColor(255, 255, 255),
                "center_circle": QColor(30, 100, 30),
                "text_color": QColor(255, 255, 255)
            },
            "warm_sepia_theme": {
                "background_arc": QColor(120, 90, 60),
                "tick_line": QColor(240, 230, 210),
                "center_circle": QColor(80, 50, 30),
                "text_color": QColor(240, 230, 210)
            },
            "ocean_blue_theme": {
                "background_arc": QColor(50, 100, 180),
                "tick_line": QColor(200, 230, 255),
                "center_circle": QColor(20, 70, 120),
                "text_color": QColor(200, 230, 255)
            },
            "vibrant_purple_theme": {
                "background_arc": QColor(100, 50, 150),
                "tick_line": QColor(255, 200, 255),
                "center_circle": QColor(60, 20, 100),
                "text_color": QColor(255, 200, 255)
            },
            "light_modern_theme": {
                "background_arc": QColor(180, 180, 180),
                "tick_line": QColor(50, 50, 50),
                "center_circle": QColor(100, 100, 100),
                "text_color": QColor(50, 50, 50)
            },
            "high_contrast_theme": {
                "background_arc": QColor(80, 80, 80),
                "tick_line": QColor(255, 255, 0), # Yellow
                "center_circle": QColor(0, 0, 0), # Black
                "text_color": QColor(255, 255, 0) # Yellow
            }
        }

        palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"]) # Fallback to dark
        
        self.bg_arc_color = palette["background_arc"]
        self.tick_line_color = palette["tick_line"]
        self.center_circle_color = palette["center_circle"]
        self.text_color = palette["text_color"] # Store for direct use in paintEvent for tick labels

        # Apply text color to labels
        self.value_label.setStyleSheet("color: {};".format(self.text_color.name()))
        self.title_label.setStyleSheet("color: {};".format(self.text_color.name()))


    def set_value(self, value):
        """
        Updates the gauge's displayed value and redraws it.
        Clamps the value between min and max.
        """
        self.current_value = max(self.min_val, min(self.max_val, value))
        self.value_label.setText("{:.1f} {}".format(self.current_value, self.unit))
        self._set_theme_colors() # Re-apply colors in case theme changed
        self.update() # Trigger repaint

    def paintEvent(self, event):
        """
        Paints the gauge arc, needle, and tick marks.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        side = min(rect.width(), rect.height())
        
        # Adjust gauge size to fit inside the widget, leaving space for labels
        # Dynamically scale gauge_size based on the available side length
        gauge_size = side * 0.8
        
        # Center the gauge
        center_x = rect.width() / 2
        center_y = rect.height() / 2 + (side * 0.1) # Slightly lower for aesthetics, gives space for title above

        # Arc properties
        start_angle = 225 * 16 # Start from bottom-left (225 degrees) in 1/16th of a degree units
        span_angle = -270 * 16 # Sweep clockwise for 270 degrees

        # Draw background arc using theme color
        painter.setPen(QPen(self.bg_arc_color, side * 0.04)) # Use dynamic color, line thickness scales with size
        painter.drawArc(QRectF(center_x - gauge_size/2, center_y - gauge_size/2, gauge_size, gauge_size), start_angle, span_angle)

        # Calculate arc for current value
        range_val = self.max_val - self.min_val
        if range_val == 0: # Avoid division by zero
            normalized_value = 0.0
        else:
            normalized_value = (self.current_value - self.min_val) / float(range_val)
        current_span = int(span_angle * normalized_value)
        
        # Set color based on value (example: green for good, yellow for warning, red for critical)
        if normalized_value < 0.6:
            indicator_color = QColor(60, 200, 60) # Green
        elif normalized_value < 0.85:
            indicator_color = QColor(255, 200, 0) # Yellow
        else:
            indicator_color = QColor(255, 60, 60) # Red

        # Draw value arc
        painter.setPen(QPen(indicator_color, side * 0.04, cap=Qt.RoundCap)) # Line thickness scales
        painter.drawArc(QRectF(center_x - gauge_size/2, center_y - gauge_size/2, gauge_size, gauge_size), start_angle, current_span)

        # Draw tick marks and labels using theme color
        painter.setPen(QPen(self.tick_line_color, 2)) # Use dynamic color
        
        # Dynamically adjust font size for tick labels and value label
        font_size_ticks = int(side * 0.05)
        font_size_value = int(side * 0.1)
        font_size_title = int(side * 0.07) # Adjust title font size

        # Ensure minimum font sizes for readability
        if font_size_ticks < 8: font_size_ticks = 8
        if font_size_value < 16: font_size_value = 16
        if font_size_title < 12: font_size_title = 12


        font_ticks = QFont("Inter", font_size_ticks)
        painter.setFont(font_ticks)
        self.value_label.setFont(QFont("Inter", font_size_value, QFont.Bold))
        self.title_label.setFont(QFont("Inter", font_size_title))

        radius = gauge_size / 2
        num_ticks = 10
        tick_length = side * 0.02
        
        for i in range(num_ticks + 1):
            angle = start_angle / 16.0 + (span_angle / 16.0) * (float(i) / num_ticks)
            
            # Convert angle to radians for trigonometric functions
            angle_rad = angle * (math.pi / 180.0) # Use math.pi
            
            # Outer point of tick
            x1 = center_x + radius * math.cos(angle_rad) # Use math.cos
            y1 = center_y + radius * math.sin(angle_rad) # Use math.sin
            
            # Inner point of tick
            x2 = center_x + (radius - tick_length) * math.cos(angle_rad) # Use math.cos
            y2 = center_y + (radius - tick_length) * math.sin(angle_rad) # Use math.sin
            
            painter.drawLine(QPointF(x1, y1), QPointF(x2, y2))

            # Draw tick labels (min, max, and some in between)
            if i == 0 or i == num_ticks or i == num_ticks // 2: # Use integer division for Python 3.5 compatibility
                value_at_tick = self.min_val + (self.max_val - self.min_val) * (float(i) / num_ticks)
                
                # Position text slightly further out from the tick
                text_radius = radius + tick_length
                text_x = center_x + text_radius * math.cos(angle_rad) # Use math.cos
                text_y = center_y + text_radius * math.sin(angle_rad) # Use math.sin
                
                # Create a small bounding rectangle for the text to ensure alignment
                text_rect_width = side * 0.2 # Scale text rect width
                text_rect_height = side * 0.1 # Scale text rect height
                text_rect = QRectF(text_x - text_rect_width / 2, text_y - text_rect_height / 2, text_rect_width, text_rect_height)
                
                # Further adjust text position slightly to avoid overlapping with tick marks
                # This is a heuristic and might need fine-tuning for different gauge sizes
                adjust_x = math.cos(angle_rad) * (tick_length / 2) # Use math.cos
                adjust_y = math.sin(angle_rad) * (tick_length / 2) # Use math.sin
                text_rect.translate(adjust_x, adjust_y)

                painter.setPen(QPen(self.text_color)) # Use dynamic color for tick labels
                painter.drawText(text_rect, Qt.AlignCenter, "{:.0f}".format(value_at_tick))
                painter.setPen(QPen(self.tick_line_color, 2)) # Reset pen for tick lines


        # Draw needle (triangle)
        needle_length = radius * 0.7
        needle_width = side * 0.03
        
        # Current angle for the needle
        needle_angle = start_angle / 16.0 + normalized_value * (span_angle / 16.0)
        needle_angle_rad = needle_angle * (math.pi / 180.0) # Use math.pi

        # Needle tip
        tip_x = center_x + needle_length * math.cos(needle_angle_rad) # Use math.cos
        tip_y = center_y + needle_length * math.sin(needle_angle_rad) # Use math.sin

        # Base points of the needle (perpendicular to the needle direction)
        # We need to find points on a small circle around the center, offset by 90 degrees
        base_angle_offset_rad = 90 * (math.pi / 180.0) # Use math.pi
        
        base_left_x = center_x + needle_width * math.cos(needle_angle_rad - base_angle_offset_rad) # Use math.cos
        base_left_y = center_y + needle_width * math.sin(needle_angle_rad - base_angle_offset_rad) # Use math.sin
        
        base_right_x = center_x + needle_width * math.cos(needle_angle_rad + base_angle_offset_rad) # Use math.cos
        base_right_y = center_y + needle_width * math.sin(needle_angle_rad + base_angle_offset_rad) # Use math.sin

        needle_path = QPainterPath()
        needle_path.moveTo(QPointF(tip_x, tip_y))
        needle_path.lineTo(QPointF(base_left_x, base_left_y))
        needle_path.lineTo(QPointF(base_right_x, base_right_y))
        needle_path.closeSubpath()

        painter.setBrush(QBrush(indicator_color))
        painter.setPen(Qt.NoPen)
        painter.drawPath(needle_path)

        # Draw center circle using theme color
        painter.setBrush(QBrush(self.center_circle_color)) # Use dynamic color
        painter.drawEllipse(QPointF(center_x, center_y), side * 0.05, side * 0.05)
