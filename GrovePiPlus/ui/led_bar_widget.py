# ui/led_bar_widget.py
from PyQt5.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt5.QtCore import Qt, QSize

from utils.config_manager import ConfigManager # Import ConfigManager

class LEDBarWidget(QWidget):
    """
    A custom widget to visually represent an LED bar with 10 segments.
    """
    def __init__(self, title="LED Bar", segments=10, config_manager=None, parent=None): # Added config_manager
        super(LEDBarWidget, self).__init__(parent)
        self.segments = segments
        self.lit_segments = 0 # Number of currently lit segments (0-10)
        self.title = title

        self.config = config_manager if config_manager else ConfigManager.get_instance() # Get config instance

        self.setMinimumSize(250, 80)
        self.setMaximumHeight(100) # Keep it compact

        self.layout = QVBoxLayout(self)
        self.title_label = QLabel(self.title)
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setFont(QFont("Inter", 12))
        self.layout.addWidget(self.title_label)

        self.led_layout = QHBoxLayout()
        self.layout.addLayout(self.led_layout)
        self.layout.addStretch(1) # Push content to top

        self.setToolTip(self.title)
        self._set_theme_colors() # Set initial theme colors

    def _set_theme_colors(self):
        """Sets internal color attributes based on the current theme."""
        current_theme = self.config.get_setting("current_theme", "dark_theme")

        theme_palettes = {
            "dark_theme": {
                "off_led": QColor(50, 50, 50),
                "border": QColor(30, 30, 30),
                "text": QColor(171, 178, 191)
            },
            "light_theme": {
                "off_led": QColor(200, 200, 200),
                "border": QColor(150, 150, 150),
                "text": QColor(51, 51, 51)
            },
            "blue_theme": {
                "off_led": QColor(40, 60, 80),
                "border": QColor(20, 30, 40),
                "text": QColor(224, 242, 247)
            },
            "dark_gray_theme": {
                "off_led": QColor(60, 60, 60),
                "border": QColor(40, 40, 40),
                "text": QColor(240, 240, 240)
            },
            "forest_green_theme": {
                "off_led": QColor(30, 80, 30),
                "border": QColor(20, 50, 20),
                "text": QColor(255, 255, 255)
            },
            "warm_sepia_theme": {
                "off_led": QColor(90, 70, 50),
                "border": QColor(70, 50, 30),
                "text": QColor(240, 230, 210)
            },
            "ocean_blue_theme": {
                "off_led": QColor(30, 70, 110),
                "border": QColor(10, 40, 80),
                "text": QColor(200, 230, 255)
            },
            "vibrant_purple_theme": {
                "off_led": QColor(70, 30, 100),
                "border": QColor(40, 10, 60),
                "text": QColor(255, 200, 255)
            },
            "light_modern_theme": {
                "off_led": QColor(200, 200, 200),
                "border": QColor(150, 150, 150),
                "text": QColor(50, 50, 50)
            },
            "high_contrast_theme": {
                "off_led": QColor(30, 30, 30),
                "border": QColor(10, 10, 10),
                "text": QColor(255, 255, 0)
            }
        }

        palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"]) # Fallback to dark
        
        self.off_led_color = palette["off_led"]
        self.led_border_color = palette["border"]
        text_color = palette["text"]

        self.title_label.setStyleSheet("color: {};".format(text_color.name()))


    def set_lit_segments(self, count):
        """
        Sets the number of lit segments on the LED bar (0-10).
        """
        self.lit_segments = max(0, min(self.segments, count))
        self.update() # Trigger repaint

    def paintEvent(self, event):
        """
        Paints the individual LED segments.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        rect = self.rect()
        
        # Calculate available width for LEDs
        padding = 10
        available_width = rect.width() - (2 * padding)
        
        # Calculate LED size based on available width and number of segments
        led_spacing = 5 # Space between LEDs
        # Ensure led_width is not negative if available_width is too small
        if self.segments > 0:
            led_width = (available_width - (self.segments - 1) * led_spacing) / float(self.segments)
        else:
            led_width = 0 # No segments to draw

        led_height = self.height() * 0.3 # Make LEDs a percentage of widget height

        start_x = padding
        # Vertically center the LEDs
        start_y = (rect.height() / 2) - (led_height / 2) + 10 # Offset for title label

        for i in range(self.segments):
            # Determine LED color
            if i < self.lit_segments:
                # Lit color (e.g., green for lower, yellow for mid, red for higher)
                if i < 4:
                    led_color = QColor(60, 200, 60) # Green
                elif i < 7:
                    led_color = QColor(255, 200, 0) # Yellow
                else:
                    led_color = QColor(255, 60, 60) # Red
            else:
                led_color = self.off_led_color # Use theme-aware off color

            # Draw the LED rectangle
            painter.setBrush(QBrush(led_color))
            painter.setPen(QPen(self.led_border_color, 1)) # Use theme-aware border color
            
            # Make the LEDs rounded
            painter.drawRoundedRect(start_x, start_y, led_width, led_height, 5, 5)

            # Move to the next LED position
            start_x += led_width + led_spacing
