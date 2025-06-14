# ui/gauge_widget.py
import math # Import the math module for trigonometric functions
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy # Import QSizePolicy
from PyQt5.QtGui import QPainter, QColor, QFont, QPen, QBrush, QPainterPath
from PyQt5.QtCore import Qt, QRectF, QPointF, QSize

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

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding) # Changed to Expanding for full responsiveness

        self.layout = QVBoxLayout(self)
        self.value_label = QLabel("{:.1f} {}".format(self.current_value, self.unit))
        self.value_label.setAlignment(Qt.AlignCenter)
        self.value_label.setFont(QFont("Inter", 16, QFont.Bold))
        
        # Make value label itself expand
        self.value_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.value_label.setContentsMargins(0,0,0,0) # Remove any default margins

        self.layout.addWidget(self.value_label)
        self.layout.setContentsMargins(0,0,0,0) # Remove default layout margins

        # Call _set_theme_colors AFTER self.value_label has been created
        self._set_theme_colors()


    def _set_theme_colors(self):
        """
        Sets the theme-specific colors for the gauge.
        """
        current_theme = self.config.get_setting("current_theme", "dark_theme")
        theme_palettes = {
            "dark_theme": {
                "background_color": QColor(50, 50, 50),
                "border_color": QColor(80, 80, 80),
                "text_color": QColor("#E0E0E0"),
                "fill_color": QColor("#00BFFF"), # Default fill color
                "needle_color": QColor("#FFD700") # Gold
            },
            "light_theme": {
                "background_color": QColor(240, 240, 240),
                "border_color": QColor(180, 180, 180),
                "text_color": QColor("#333333"),
                "fill_color": QColor("#007bff"),
                "needle_color": QColor("#FF8C00") # Dark Orange
            },
            "blue_theme": {
                "background_color": QColor("#264264"),
                "border_color": QColor("#3c6595"),
                "text_color": QColor("#e0f2f7"),
                "fill_color": QColor("#4682B4"),
                "needle_color": QColor("#F0A000") # Amber
            },
            "dark_gray_theme": {
                "background_color": QColor("#4B4F52"),
                "border_color": QColor("#6C7072"),
                "text_color": QColor("#fdfdfd"),
                "fill_color": QColor("#6a737d"),
                "needle_color": QColor("#FFD700")
            },
            "forest_green_theme": {
                "background_color": QColor("#2E7D32"),
                "border_color": QColor("#4CAF50"),
                "text_color": QColor("#FFFFFF"),
                "fill_color": QColor("#66BB6A"),
                "needle_color": QColor("#FFD700")
            },
            "warm_sepia_theme": {
                "background_color": QColor("#5A2D0C"),
                "border_color": QColor("#A0522D"),
                "text_color": QColor("#F5DEB3"),
                "fill_color": QColor("#A0522D"),
                "needle_color": QColor("#FFD700")
            },
            "ocean_blue_theme": {
                "background_color": QColor("#002244"),
                "border_color": QColor("#005099"),
                "text_color": QColor("#E0FFFF"),
                "fill_color": QColor("#4682B4"),
                "needle_color": QColor("#FFD700")
            },
            "vibrant_purple_theme": {
                "background_color": QColor("#300050"),
                "border_color": QColor("#8A2BE2"),
                "text_color": QColor("#E6E6FA"),
                "fill_color": QColor("#8A2BE2"),
                "needle_color": QColor("#FFD700")
            },
            "light_modern_theme": {
                "background_color": QColor("#F8F8F8"),
                "border_color": QColor("#C0C0C0"),
                "text_color": QColor("#333333"),
                "fill_color": QColor("#607D8B"),
                "needle_color": QColor("#FF8C00")
            },
            "high_contrast_theme": {
                "background_color": QColor("#111111"),
                "border_color": QColor("#FF00FF"),
                "text_color": QColor("#FFFF00"),
                "fill_color": QColor("#00FF00"),
                "needle_color": QColor("#FF0000")
            }
        }

        palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"])

        self.background_color = palette["background_color"]
        self.border_color = palette["border_color"]
        self.text_color = palette["text_color"]
        self.fill_color = palette["fill_color"]
        self.needle_color = palette["needle_color"]

        # Update the QLabel's stylesheet based on the new text color
        self.value_label.setStyleSheet("color: {};".format(self.text_color.name()))
        self.update() # Trigger repaint of the custom drawn elements


    def set_value(self, value):
        """
        Sets the current value of the gauge and triggers a repaint.
        """
        if value is not None and not math.isnan(value):
            # Clamp value to be within min_val and max_val
            self.current_value = max(self.min_val, min(self.max_val, value))
            self.value_label.setText("{:.1f} {}".format(self.current_value, self.unit))
        else:
            self.current_value = float('nan') # Indicate no valid data
            self.value_label.setText("-- {}".format(self.unit)) # Display "--" if no data
        self.update() # Trigger a repaint of the custom drawn elements

    def paintEvent(self, event):
        """
        Paints the gauge, including the arc, value text, and needle.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        side = min(rect.width(), rect.height())

        # Scale the painter to a virtual 200x200 canvas.
        # This allows all drawing coordinates to be defined relative to a 200x200 square,
        # and they will automatically scale to the actual widget size.
        painter.translate(rect.center())
        painter.scale(side / 200.0, side / 200.0)
        painter.translate(-100, -100) # Translate back so (0,0) is top-left of virtual 200x200 canvas

        # Define the bounding rectangle for the arc
        arc_rect = QRectF(10, 10, 180, 180) # Virtual 200x200 canvas, centered 180x180 arc

        # Draw the background arc
        painter.setPen(QPen(self.border_color, 8)) # Use border_color for the background track
        painter.drawArc(arc_rect, 225 * 16, -270 * 16) # Arc from 225 to -45 (270 degrees total)

        # Draw the filled arc based on the current value
        if not math.isnan(self.current_value):
            angle_range = 270 # Total degrees for the gauge
            value_range = self.max_val - self.min_val
            
            # Calculate the angle based on the current value
            # Ensure value is within bounds for correct angle calculation
            clamped_value = max(self.min_val, min(self.max_val, self.current_value))
            
            if value_range > 0:
                # Normalize value to a 0-1 scale, then map to angle range
                normalized_value = (clamped_value - self.min_val) / value_range
                fill_angle = -int(normalized_value * angle_range) # Negative for counter-clockwise
            else:
                fill_angle = 0 # Avoid division by zero, no fill if range is 0

            painter.setPen(QPen(self.fill_color, 8)) # Use fill_color for the active filled part
            painter.drawArc(arc_rect, 225 * 16, fill_angle * 16)

        # Draw the needle
        painter.setPen(QPen(self.needle_color, 2))
        painter.setBrush(QBrush(self.needle_color))

        center_x, center_y = 100, 100 # Center of the virtual 200x200 canvas
        needle_length = 70 # Length of the needle in virtual units
        needle_width = 5 # Width of the needle's base in virtual units

        # Calculate needle angle based on value (0 degrees is horizontal right, increases clockwise)
        # The gauge goes from 225 degrees (bottom left) to -45 degrees (bottom right)
        # So, 0% is at 225 degrees, 100% is at -45 degrees. Total span is 270 degrees.
        angle_at_zero_val = 225 # degrees
        angle_span = 270 # degrees

        # Calculate current angle
        value_normalized = (self.current_value - self.min_val) / (self.max_val - self.min_val)
        # Ensure value_normalized is between 0 and 1
        value_normalized = max(0.0, min(1.0, value_normalized))
        
        # Angle decreases as value increases (counter-clockwise movement from start_angle 225)
        needle_angle_deg = angle_at_zero_val - (value_normalized * angle_span)
        needle_angle_rad = needle_angle_deg * (math.pi / 180.0) # Convert to radians for math functions

        # Needle tip
        tip_x = center_x + needle_length * math.cos(needle_angle_rad) # Use math.cos
        tip_y = center_y - needle_length * math.sin(needle_angle_rad) # Use math.sin (Y-axis is inverted in Qt)

        # Base points of the needle (perpendicular to the needle direction)
        # We need to find points on a small circle around the center, offset by 90 degrees
        base_angle_offset_rad = 90 * (math.pi / 180.0) # Use math.pi
        
        base_left_x = center_x + needle_width * math.cos(needle_angle_rad + base_angle_offset_rad) # Use math.cos
        base_left_y = center_y - needle_width * math.sin(needle_angle_rad + base_angle_offset_rad) # Use math.sin
        
        base_right_x = center_x + needle_width * math.cos(needle_angle_rad - base_angle_offset_rad) # Use math.cos
        base_right_y = center_y - needle_width * math.sin(needle_angle_rad - base_angle_offset_rad) # Use math.sin

        needle_path = QPainterPath()
        needle_path.moveTo(QPointF(tip_x, tip_y))
        needle_path.lineTo(QPointF(base_left_x, base_left_y))
        needle_path.lineTo(QPointF(base_right_x, base_right_y))
        needle_path.closeSubpath()

        painter.drawPath(needle_path)

        # Draw the central circle (pivot for the needle)
        painter.setBrush(QBrush(self.needle_color))
        painter.drawEllipse(QPointF(center_x, center_y), needle_width * 1.5, needle_width * 1.5) # Larger circle at pivot

        # The value_label is handled by the QLabel, which will position itself
        # based on the layout and its size policy.
        # Its text and color are updated in set_value and _set_theme_colors.

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
