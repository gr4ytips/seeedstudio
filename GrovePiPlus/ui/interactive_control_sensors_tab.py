# ui/interactive_control_sensors_tab.py
import os
import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QHBoxLayout, QPushButton, QSlider, QFrame, QSizePolicy # Import QSizePolicy
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QColor # Import QColor

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from ui.gauge_widget import GaugeWidget
from ui.led_bar_widget import LEDBarWidget
from utils.logger import Logger
from utils.config_manager import ConfigManager # Import ConfigManager

class InteractiveControlSensorsTab(QWidget):
    """
    Separate tab to display and control interactive sensors:
    Button, Relay, LED Bar, and Rotary Angle.
    """
    def __init__(self, sensor_manager, parent=None):
        # Corrected: Use InteractiveControlSensorsTab instead of InteractiveControlSensors in super()
        super(InteractiveControlSensorsTab, self).__init__(parent)
        self.logger = Logger.get_logger()
        self.sensor_manager = sensor_manager
        self.config = ConfigManager.get_instance() # Get config instance here

        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)
        
        self._set_theme_colors() # Set initial theme colors
        self._setup_ui()
        self.set_style()
        self.logger.info("InteractiveControlSensorsTab initialized.")

    def _set_theme_colors(self):
        """Sets internal color attributes based on the current theme for dynamic elements."""
        current_theme = self.config.get_setting("current_theme", "dark_theme")

        # Define color palettes for various themes
        theme_palettes = {
            "dark_theme": {
                "title_color": QColor("#ADD8E6"), # Light Blue
                "label_color": QColor("#abb2bf"),
                "frame_border": QColor("#666"),
                "frame_bg": QColor("rgba(30, 30, 30, 0.7)"),
                "tab_background": QColor("#21252b"), # Matches QTabWidget::pane for dark theme
                "button_bg": QColor("#4CAF50"), # Green
                "button_hover_bg": QColor("#45a049"),
                "button_pressed_bg": QColor("#367c39"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#999999"),
                "slider_groove_bg": QColor("#555"),
                "slider_handle_bg": QColor("#DDD"),
                "slider_handle_border": QColor("#AAA"),
                "slider_subpage_bg": QColor("#1E90FF"), # DodgerBlue
                "warning_text": QColor("#FF4500"), # OrangeRed
                "success_text": QColor("#7CFC00"), # LimeGreen
            },
            "light_theme": {
                "title_color": QColor("#007bff"),
                "label_color": QColor("#333333"),
                "frame_border": QColor("#ccc"),
                "frame_bg": QColor("rgba(255, 255, 255, 0.7)"),
                "tab_background": QColor("#ffffff"), # Matches QTabWidget::pane for light theme
                "button_bg": QColor("#28a745"),
                "button_hover_bg": QColor("#218838"),
                "button_pressed_bg": QColor("#1e7e34"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#ccc"),
                "slider_groove_bg": QColor("#eee"),
                "slider_handle_bg": QColor("#6c757d"),
                "slider_handle_border": QColor("#5a6268"),
                "slider_subpage_bg": QColor("#007bff"),
                "warning_text": QColor("#dc3545"),
                "success_text": QColor("#28a745"),
            },
             "blue_theme": {
                "title_color": QColor("#87CEEB"),
                "label_color": QColor("#e0f2f7"),
                "frame_border": QColor("#3c6595"),
                "frame_bg": QColor("rgba(26, 42, 64, 0.7)"),
                "tab_background": QColor("#152535"), # Matches QTabWidget::pane for blue theme
                "button_bg": QColor("#4682B4"),
                "button_hover_bg": QColor("#3a719d"),
                "button_pressed_bg": QColor("#306080"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#3c6595"),
                "slider_groove_bg": QColor("#2b4a68"),
                "slider_handle_bg": QColor("#87CEEB"),
                "slider_handle_border": QColor("#4682B4"),
                "slider_subpage_bg": QColor("#4682B4"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#3CB371"),
            },
            "dark_gray_theme": {
                "title_color": QColor("#79c0ff"),
                "label_color": QColor("#fdfdfd"),
                "frame_border": QColor("#666"),
                "frame_bg": QColor("rgba(60, 63, 65, 0.7)"),
                "tab_background": QColor("#333333"), # Matches QTabWidget::pane for dark gray theme
                "button_bg": QColor("#6a737d"),
                "button_hover_bg": QColor("#586069"),
                "button_pressed_bg": QColor("#4d5358"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#505050"),
                "slider_groove_bg": QColor("#444"),
                "slider_handle_bg": QColor("#fdfdfd"),
                "slider_handle_border": QColor("#888"),
                "slider_subpage_bg": QColor("#6a737d"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#3CB371"),
            },
            "forest_green_theme": {
                "title_color": QColor("#A5D6A7"),
                "label_color": QColor("#FFFFFF"),
                "frame_border": QColor("#66BB6A"),
                "frame_bg": QColor("rgba(34, 139, 34, 0.7)"),
                "tab_background": QColor("#1B5E20"), # Matches QTabWidget::pane for forest green theme
                "button_bg": QColor("#66BB6A"),
                "button_hover_bg": QColor("#4CAF50"),
                "button_pressed_bg": QColor("#388E3C"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#4CAF50"),
                "slider_groove_bg": QColor("#388E3C"),
                "slider_handle_bg": QColor("#FFFFFF"),
                "slider_handle_border": QColor("#A5D6A7"),
                "slider_subpage_bg": QColor("#66BB6A"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#9ACD32"),
            },
            "warm_sepia_theme": {
                "title_color": QColor("#DEB887"),
                "label_color": QColor("#F5DEB3"),
                "frame_border": QColor("#A0522D"),
                "frame_bg": QColor("rgba(112, 66, 20, 0.7)"),
                "tab_background": QColor("#5A2D0C"), # Matches QTabWidget::pane for warm sepia theme
                "button_bg": QColor("#A0522D"),
                "button_hover_bg": QColor("#8B4513"),
                "button_pressed_bg": QColor("#7C4F2A"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#A0522D"),
                "slider_groove_bg": QColor("#8B4513"),
                "slider_handle_bg": QColor("#F5DEB3"),
                "slider_handle_border": QColor("#DEB887"),
                "slider_subpage_bg": QColor("#A0522D"),
                "warning_text": QColor("#CD5C5C"),
                "success_text": QColor("#6B8E23"),
            },
            "ocean_blue_theme": {
                "title_color": QColor("#87CEEB"),
                "label_color": QColor("#E0FFFF"),
                "frame_border": QColor("#0066CC"),
                "frame_bg": QColor("rgba(0, 51, 102, 0.7)"),
                "tab_background": QColor("#002244"), # Matches QTabWidget::pane for ocean blue theme
                "button_bg": QColor("#4682B4"),
                "button_hover_bg": QColor("#3A719D"),
                "button_pressed_bg": QColor("#2A6080"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#005099"),
                "slider_groove_bg": QColor("#004488"),
                "slider_handle_bg": QColor("#E0FFFF"),
                "slider_handle_border": QColor("#87CEEB"),
                "slider_subpage_bg": QColor("#4682B4"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#66CDAA"),
            },
            "vibrant_purple_theme": {
                "title_color": QColor("#DDA0DD"),
                "label_color": QColor("#E6E6FA"),
                "frame_border": QColor("#8A2BE2"),
                "frame_bg": QColor("rgba(75, 0, 130, 0.7)"),
                "tab_background": QColor("#300050"), # Matches QTabWidget::pane for vibrant purple theme
                "button_bg": QColor("#8A2BE2"),
                "button_hover_bg": QColor("#7B1BE0"),
                "button_pressed_bg": QColor("#6A0DAD"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#8A2BE2"),
                "slider_groove_bg": QColor("#6A0DAD"),
                "slider_handle_bg": QColor("#E6E6FA"),
                "slider_handle_border": QColor("#DDA0DD"),
                "slider_subpage_bg": QColor("#8A2BE2"),
                "warning_text": QColor("#FF6347"),
                "success_text": QColor("#7FFF00"),
            },
            "light_modern_theme": {
                "title_color": QColor("#555555"),
                "label_color": QColor("#333333"),
                "frame_border": QColor("#A0A0A0"),
                "frame_bg": QColor("rgba(248, 248, 248, 0.9)"),
                "tab_background": QColor("#F8F8F8"), # Matches QTabWidget::pane for light modern theme
                "button_bg": QColor("#607D8B"),
                "button_hover_bg": QColor("#455A64"),
                "button_pressed_bg": QColor("#37474F"),
                "button_text": QColor("white"),
                "slider_groove_border": QColor("#C0C0C0"),
                "slider_groove_bg": QColor("#E8E8E8"),
                "slider_handle_bg": QColor("#FFFFFF"),
                "slider_handle_border": QColor("#90A4AE"),
                "slider_subpage_bg": QColor("#607D8B"),
                "warning_text": QColor("#FF4500"),
                "success_text": QColor("#28A745"),
            },
            "high_contrast_theme": {
                "title_color": QColor("#FF0000"),
                "label_color": QColor("#FFFF00"),
                "frame_border": QColor("#00FFFF"),
                "frame_bg": QColor("rgba(0, 0, 0, 0.9)"),
                "tab_background": QColor("#111111"), # Matches QTabWidget::pane for high contrast theme
                "button_bg": QColor("#FF00FF"),
                "button_hover_bg": QColor("#CC00CC"),
                "button_pressed_bg": QColor("#990099"),
                "button_text": QColor("#000000"),
                "slider_groove_border": QColor("#FF00FF"),
                "slider_groove_bg": QColor("#333333"),
                "slider_handle_bg": QColor("#FFFF00"),
                "slider_handle_border": QColor("#00FFFF"),
                "slider_subpage_bg": QColor("#FFFF00"),
                "warning_text": QColor("#FF0000"),
                "success_text": QColor("#00FF00"),
            }
        }

        self.theme_palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"])
        
        self.title_color = self.theme_palette["title_color"]
        self.label_color = self.theme_palette["label_color"]
        self.frame_border_color = self.theme_palette["frame_border"]
        self.frame_bg_color = self.theme_palette["frame_bg"]
        self.tab_background_color = self.theme_palette["tab_background"] # New attribute for tab background
        self.button_bg_color = self.theme_palette["button_bg"]
        self.button_hover_bg_color = self.theme_palette["button_hover_bg"]
        self.button_pressed_bg_color = self.theme_palette["button_pressed_bg"]
        self.button_text_color = self.theme_palette["button_text"]
        self.slider_groove_border_color = self.theme_palette["slider_groove_border"]
        self.slider_groove_bg_color = self.theme_palette["slider_groove_bg"]
        self.slider_handle_bg_color = self.theme_palette["slider_handle_bg"]
        self.slider_handle_border_color = self.theme_palette["slider_handle_border"]
        self.slider_subpage_bg_color = self.theme_palette["slider_subpage_bg"]
        self.warning_text_color = self.theme_palette["warning_text"]
        self.success_text_color = self.theme_palette["success_text"]

        # Apply colors to existing widgets
        if hasattr(self, 'title_label'):
            self.title_label.setStyleSheet("color: {};".format(self.title_color.name()))
        if hasattr(self, 'button_read_label'):
            # Update button_read_label based on its current state (if applicable)
            button_state_color = self.success_text_color if self.button_read_label.text() == "ON" else self.warning_text_color
            self.button_read_label.setStyleSheet("color: {};".format(button_state_color.name()))
        if hasattr(self, 'relay_button'):
             # Update relay button background based on its current state
            relay_button_bg_color = self.success_text_color if self.relay_state == 1 else self.warning_text_color
            self.relay_button.setStyleSheet("background-color: {}; color: {};".format(relay_button_bg_color.name(), self.button_text_color.name()))
        if hasattr(self, 'led_bar_widget'):
            self.led_bar_widget._set_theme_colors() # Call its own theme setter
        if hasattr(self, 'rotary_angle_gauge'):
            self.rotary_angle_gauge._set_theme_colors() # Call its own theme setter

        # Re-apply stylesheet to ensure all QSS rules with dynamic colors are updated
        self.set_style()


    def _setup_ui(self):
        """Sets up the UI elements for the interactive control sensors tab."""
        self.title_label = QLabel("Interactive Controls: Button, Relay, LED Bar, Rotary Angle")
        self.title_label.setFont(QFont("Inter", 20, QFont.Bold))
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setContentsMargins(0, 20, 0, 20)
        self.main_layout.addWidget(self.title_label)

        self.content_frame = QFrame(self)
        self.content_frame.setFrameShape(QFrame.StyledPanel)
        self.content_frame.setFrameShadow(QFrame.Raised)
        self.content_frame.setObjectName("contentFrame")
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setAlignment(Qt.AlignCenter)
        content_layout.setContentsMargins(50, 50, 50, 50) # Add some padding to the content frame

        # Row 1: Button and Rotary Angle
        row1_layout = QHBoxLayout()
        row1_layout.setAlignment(Qt.AlignCenter)
        row1_layout.setStretch(0, 1) # Give equal stretch to both sides
        row1_layout.setStretch(1, 1)


        # Button Status
        button_group_layout = QVBoxLayout()
        button_group_label = QLabel("Button Status")
        button_group_label.setFont(QFont("Inter", 16, QFont.Bold))
        button_group_label.setAlignment(Qt.AlignCenter)
        button_group_layout.addWidget(button_group_label)
        self.button_read_label = QLabel("OFF")
        self.button_read_label.setFont(QFont("Inter", 36, QFont.Bold))
        self.button_read_label.setAlignment(Qt.AlignCenter)
        self.button_read_label.setObjectName("buttonReadLabel") # Add object name for styling
        button_group_layout.addWidget(self.button_read_label)
        button_group_layout.addStretch(1) # Allows button status to push up
        row1_layout.addLayout(button_group_layout)
        row1_layout.addSpacing(50)

        # Rotary Angle Gauge
        self.rotary_angle_gauge = GaugeWidget("Rotary Angle", "raw", 0, 1023, config_manager=self.config) # Pass config_manager
        # Set size policy to expanding to allow resizing
        self.rotary_angle_gauge.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.rotary_angle_gauge.setMinimumSize(150, 150) # Reduced minimum for better responsiveness
        self.rotary_angle_gauge.setMaximumSize(350, 350) # Increased maximum size
        row1_layout.addWidget(self.rotary_angle_gauge)

        content_layout.addLayout(row1_layout)
        content_layout.addSpacing(30) # Space between rows

        # Row 2: Relay and LED Bar Controls
        row2_layout = QHBoxLayout()
        row2_layout.setAlignment(Qt.AlignCenter)
        row2_layout.setStretch(0, 1) # Give equal stretch to both sides
        row2_layout.setStretch(1, 1)

        # Relay Control
        relay_group_layout = QVBoxLayout()
        relay_group_label = QLabel("Relay Control")
        relay_group_label.setFont(QFont("Inter", 16, QFont.Bold))
        relay_group_label.setAlignment(Qt.AlignCenter)
        relay_group_layout.addWidget(relay_group_label)
        
        self.relay_button = QPushButton("Toggle Relay (OFF)")
        self.relay_button.setFont(QFont("Inter", 14, QFont.Bold))
        self.relay_button.setFixedSize(200, 60) # Keep fixed size for buttons for consistency
        self.relay_button.clicked.connect(self._toggle_relay)
        self.relay_button.setObjectName("relayButton") # Add object name for styling
        self.relay_state = 0 # 0: OFF, 1: ON
        relay_group_layout.addWidget(self.relay_button, alignment=Qt.AlignCenter)
        relay_group_layout.addStretch(1) # Allows relay control to push up
        row2_layout.addLayout(relay_group_layout)
        row2_layout.addSpacing(50)

        # LED Bar Control
        led_bar_group_layout = QVBoxLayout()
        led_bar_group_label = QLabel("LED Bar Control (0-10)")
        led_bar_group_label.setFont(QFont("Inter", 16, QFont.Bold))
        led_bar_group_label.setAlignment(Qt.AlignCenter)
        led_bar_group_layout.addWidget(led_bar_group_label)
        
        self.led_bar_widget = LEDBarWidget("LED Bar Visual", segments=10, config_manager=self.config) # Pass config_manager
        self.led_bar_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.led_bar_widget.setMinimumSize(200, 80) # Reduced minimum width
        self.led_bar_widget.setMaximumHeight(150) # Increased maximum height
        led_bar_group_layout.addWidget(self.led_bar_widget, alignment=Qt.AlignCenter)

        self.led_bar_slider = QSlider(Qt.Horizontal)
        self.led_bar_slider.setMinimum(0)
        self.led_bar_slider.setMaximum(10)
        self.led_bar_slider.setValue(0)
        self.led_bar_slider.setTickPosition(QSlider.TicksBelow)
        self.led_bar_slider.setTickInterval(1)
        self.led_bar_slider.setSingleStep(1)
        # self.led_bar_slider.setFixedSize(300, 40) # Removed fixed size for responsiveness
        self.led_bar_slider.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed) # Allow horizontal expansion
        self.led_bar_slider.valueChanged.connect(self._control_led_bar) # Reverted to valueChanged
        self.led_bar_slider.setObjectName("ledBarSlider") # Add object name for styling
        led_bar_group_layout.addWidget(self.led_bar_slider, alignment=Qt.AlignCenter)
        led_bar_group_layout.addStretch(1) # Allows LED bar controls to push up
        row2_layout.addLayout(led_bar_group_layout)

        content_layout.addLayout(row2_layout)
        
        self.main_layout.addWidget(self.content_frame, alignment=Qt.AlignCenter) 
        self.main_layout.addStretch(1) # Add a stretch to the main layout to push content to top if needed,
                                        # but also allows content_frame to expand.

    def _toggle_relay(self):
        """Toggles the state of the relay."""
        new_state = 1 - self.relay_state # Flip 0 to 1, or 1 to 0
        self.sensor_manager.control_relay(new_state)
        # The actual UI update happens via `update_relay_status` signal connected from sensor_manager

    def _control_led_bar(self, level):
        """Controls the LED bar based on slider value."""
        self.sensor_manager.control_led_bar(level)
        # The actual UI update for the custom widget happens via `update_led_bar_status`

    def update_button_status(self, state):
        """
        Updates the Button status label.
        This slot is connected to the SensorWorker's button_status_updated signal.
        """
        self.button_read_label.setText("ON" if state == 1 else "OFF")
        # Update color based on state using theme palette
        color = self.success_text_color if state == 1 else self.warning_text_color
        self.button_read_label.setStyleSheet("color: {};".format(color.name()))


    def update_relay_status(self, state):
        """
        Updates the Relay button text and internal state.
        This slot is connected to the SensorManager's relay_status_changed signal.
        """
        self.relay_state = state
        self.relay_button.setText("Toggle Relay ({})".format("ON" if state == 1 else "OFF"))
        # Update button background based on state using theme palette
        bg_color = self.button_bg_color if state == 1 else self.warning_text_color # Use warning color for OFF
        self.relay_button.setStyleSheet("background-color: {}; color: {};".format(bg_color.name(), self.button_text_color.name()))


    def update_led_bar_status(self, level):
        """
        Updates the LED Bar custom widget and slider value.
        This slot is connected to the SensorManager's led_bar_status_changed signal.
        """
        self.led_bar_widget.set_lit_segments(level)
        self.led_bar_slider.setValue(level) # Keep slider in sync

    def update_rotary_angle_data(self, raw_value):
        """
        Updates the Rotary Angle gauge.
        This slot is connected to the SensorWorker's rotary_angle_data_updated signal.
        """
        self.rotary_angle_gauge.set_value(raw_value)

    def set_style(self):
        """Applies specific styling for the tab."""
        self.setStyleSheet("""
            QWidget#InteractiveControlSensorsTab {{
                background-color: {tab_background_color}; /* Ensure the entire tab background is themed */
            }}
            QLabel {{ /* General QLabel style within this tab */
                color: {label_color};
            }}
            QLabel#buttonReadLabel {{ /* Specific styling for the button read label */
                color: {warning_text_color}; /* Initial color for OFF */
            }}
            QFrame#contentFrame {{
                border: 1px solid {frame_border_color};
                border-radius: 15px;
                background-color: {frame_bg_color};
                padding: 20px;
                /* Removed min-width and max-width for responsiveness */
            }}
            QPushButton#relayButton {{
                background-color: {button_bg_color}; /* Default/OFF color */
                color: {button_text_color};
                border-radius: 10px;
                padding: 10px 20px;
                font-size: 14px;
                border: none;
            }}
            QPushButton#relayButton:hover {{
                background-color: {button_hover_bg_color};
            }}
            QPushButton#relayButton:pressed {{
                background-color: {button_pressed_bg_color};
            }}
            QSlider#ledBarSlider::groove:horizontal {{
                border: 1px solid {slider_groove_border_color};
                height: 8px; /* the groove height */
                border-radius: 4px;
                background: {slider_groove_bg_color};
            }}
            QSlider#ledBarSlider::handle:horizontal {{
                background: {slider_handle_bg_color};
                border: 1px solid {slider_handle_border_color};
                width: 24px;
                margin: -8px 0; /* handle is 16px wide, so -8px from each side to make it 24px total */
                border-radius: 12px;
            }}
            QSlider#ledBarSlider::sub-page:horizontal {{
                background: {slider_subpage_bg_color}; /* DodgerBlue for filled part */
                border-radius: 4px;
            }}
        """.format(
            tab_background_color=self.tab_background_color.name(), # Pass the new color
            title_color=self.title_color.name(),
            label_color=self.label_color.name(),
            frame_border_color=self.frame_border_color.name(),
            frame_bg_color=self.frame_bg_color.name(),
            button_bg_color=self.button_bg_color.name(),
            button_hover_bg_color=self.button_hover_bg_color.name(),
            button_pressed_bg_color=self.button_pressed_bg_color.name(),
            button_text_color=self.button_text_color.name(),
            slider_groove_border_color=self.slider_groove_border_color.name(),
            slider_groove_bg_color=self.slider_groove_bg_color.name(),
            slider_handle_bg_color=self.slider_handle_bg_color.name(),
            slider_handle_border_color=self.slider_handle_border_color.name(),
            slider_subpage_bg_color=self.slider_subpage_bg_color.name(),
            warning_text_color=self.warning_text_color.name(),
            success_text_color=self.success_text_color.name()
        ))
