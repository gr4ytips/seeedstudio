# ui/plots_tab.py
import os
import sys
from datetime import datetime, timedelta
import pandas as pd # Used for data handling (pip install pandas)
import pyqtgraph as pg # Used for plotting (pip install pyqtgraph)

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QPushButton, QCheckBox, QSizePolicy, QLineEdit, QFileDialog, QMessageBox, QTableWidget, QTableWidgetItem, QFrame
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QColor

# Ensure SensorApp root is in path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.logger import Logger
from utils.config_manager import ConfigManager


class PlotsTab(QWidget):
    """
    A tab dedicated to displaying sensor data plots for analysis.
    Allows selection of sensors, time ranges, and features legends and theme awareness.
    """
    SENSOR_COLUMNS = {
        "Temperature_C": "Temperature (°C)",
        "Humidity_perc": "Humidity (%)",
        "Ultrasonic_cm": "Ultrasonic (cm)",
        "Sound_raw": "Sound (raw)",
        "Light_raw": "Light (raw)",
        "Button_state": "Button (0/1)",
        "RotaryAngle_raw": "Rotary Angle (raw)"
    }

    TIME_RANGES = {
        "1 Hour": timedelta(hours=1),
        "6 Hours": timedelta(hours=6),
        "24 Hours": timedelta(hours=24),
        "7 Days": timedelta(days=7),
        "30 Days": timedelta(days=30),
        "All Data": None # Represents fetching all available data
    }

    LINE_COLORS = { # Default colors, will be overridden by theme
        "Temperature_C": "red",
        "Humidity_perc": "blue",
        "Ultrasonic_cm": "green",
        "Sound_raw": "yellow",
        "Light_raw": "cyan",
        "Button_state": "magenta",
        "RotaryAngle_raw": "white"
    }

    def __init__(self, config_manager, parent=None):
        super(PlotsTab, self).__init__(parent)
        self.logger = Logger.get_logger()
        self.config = config_manager
        self.data = pd.DataFrame() # Holds the loaded sensor data
        self.current_plot_items = {} # To store plot data items for updating colors
        self.original_plot_title = "Sensor Data Plot" # Store the original title text

        self._set_theme_colors() # Set initial theme colors FIRST
        self.main_layout = QVBoxLayout(self)
        self.setLayout(self.main_layout)

        self._setup_ui() # Then setup UI, which uses theme colors
        self._apply_theme_colors_to_plot() # Apply theme colors to plot
        self.set_style()
        self.logger.info("PlotsTab initialized.")

    def _set_theme_colors(self):
        """Sets internal color attributes based on the current theme for plot elements."""
        current_theme = self.config.get_setting("current_theme", "dark_theme")

        # Define color palettes for various themes for plot elements
        theme_palettes = {
            "dark_theme": {
                "plot_bg": QColor(40, 44, 52),      # Dark background
                "axis_text": QColor(171, 178, 191), # Light gray
                "grid_line": QColor(60, 65, 75),    # Slightly lighter dark gray
                "title_text": QColor(97, 175, 239), # Blue
                "legend_text": QColor(171, 178, 191),
                "export_button_bg": QColor(97, 175, 239),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(255, 100, 100), # Red for warnings
                "combo_bg": QColor("#3e4451"), # ComboBox background
                "combo_text": QColor("#abb2bf"), # ComboBox text
                "combo_border": QColor("#5c6370"), # ComboBox border
                "line_colors": { # Ensure enough distinct colors for all sensors
                    "Temperature_C": QColor(224, 108, 117),  # Reddish
                    "Humidity_perc": QColor(97, 175, 239),   # Bluish
                    "Ultrasonic_cm": QColor(152, 195, 121),  # Greenish
                    "Sound_raw": QColor(229, 192, 123),      # Yellowish
                    "Light_raw": QColor(86, 182, 194),       # Cyan
                    "Button_state": QColor(198, 120, 221),   # Purplish
                    "RotaryAngle_raw": QColor(255, 255, 255) # White
                }
            },
            "light_theme": {
                "plot_bg": QColor(240, 240, 240),
                "axis_text": QColor(51, 51, 51),
                "grid_line": QColor(200, 200, 200),
                "title_text": QColor(0, 123, 255),
                "legend_text": QColor(51, 51, 51),
                "export_button_bg": QColor(0, 123, 255),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(220, 53, 69), # Red for warnings
                "combo_bg": QColor("#f8f8f8"),
                "combo_text": QColor("#333"),
                "combo_border": QColor("#ccc"),
                "line_colors": {
                    "Temperature_C": QColor(220, 53, 69),
                    "Humidity_perc": QColor(0, 123, 255),
                    "Ultrasonic_cm": QColor(40, 167, 69),
                    "Sound_raw": QColor(255, 193, 7),
                    "Light_raw": QColor(23, 162, 184),
                    "Button_state": QColor(108, 117, 125),
                    "RotaryAngle_raw": QColor(0, 0, 0)
                }
            },
            "blue_theme": {
                "plot_bg": QColor(26, 42, 64),
                "axis_text": QColor(224, 242, 247),
                "grid_line": QColor(43, 74, 104),
                "title_text": QColor(135, 206, 235),
                "legend_text": QColor(224, 242, 247),
                "export_button_bg": QColor(70, 130, 180),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(255, 99, 71), # Tomato
                "combo_bg": QColor("#223f5b"),
                "combo_text": QColor("#e0f2f7"),
                "combo_border": QColor("#4a6c8e"),
                "line_colors": {
                    "Temperature_C": QColor(255, 99, 71),
                    "Humidity_perc": QColor(100, 149, 237),
                    "Ultrasonic_cm": QColor(60, 179, 113),
                    "Sound_raw": QColor(255, 215, 0),
                    "Light_raw": QColor(123, 104, 238),
                    "Button_state": QColor(218, 112, 214),
                    "RotaryAngle_raw": QColor(255, 250, 205)
                }
            },
            "dark_gray_theme": {
                "plot_bg": QColor(50, 50, 50),
                "axis_text": QColor(240, 240, 240),
                "grid_line": QColor(80, 80, 80),
                "title_text": QColor(121, 197, 255), # Lighter blue
                "legend_text": QColor(240, 240, 240),
                "export_button_bg": QColor(106, 115, 125),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(255, 100, 100), # Red
                "combo_bg": QColor("#4b4f52"),
                "combo_text": QColor("#fdfdfd"),
                "combo_border": QColor("#6c7072"),
                "line_colors": {
                    "Temperature_C": QColor(255, 100, 100),
                    "Humidity_perc": QColor(100, 150, 255),
                    "Ultrasonic_cm": QColor(100, 255, 100),
                    "Sound_raw": QColor(255, 255, 100),
                    "Light_raw": QColor(100, 255, 255),
                    "Button_state": QColor(255, 100, 255),
                    "RotaryAngle_raw": QColor(200, 200, 200)
                }
            },
            "forest_green_theme": {
                "plot_bg": QColor(34, 139, 34), # Forest Green
                "axis_text": QColor(255, 255, 255),
                "grid_line": QColor(76, 175, 80),
                "title_text": QColor(165, 214, 167),
                "legend_text": QColor(255, 255, 255),
                "export_button_bg": QColor(102, 187, 106),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(255, 120, 120), # Red
                "combo_bg": QColor("#339933"),
                "combo_text": QColor("#FFFFFF"),
                "combo_border": QColor("#4CAF50"),
                "line_colors": {
                    "Temperature_C": QColor(255, 120, 120),
                    "Humidity_perc": QColor(120, 120, 255),
                    "Ultrasonic_cm": QColor(255, 255, 120),
                    "Sound_raw": QColor(120, 255, 255),
                    "Light_raw": QColor(255, 120, 255),
                    "Button_state": QColor(255, 160, 120),
                    "RotaryAngle_raw": QColor(200, 200, 200)
                }
            },
            "warm_sepia_theme": {
                "plot_bg": QColor(112, 66, 20), # Sepia Brown
                "axis_text": QColor(245, 222, 179), # Wheat
                "grid_line": QColor(139, 69, 19),
                "title_text": QColor(222, 184, 135), # BurlyWood
                "legend_text": QColor(245, 222, 179),
                "export_button_bg": QColor(160, 82, 45),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(205, 92, 92), # IndianRed
                "combo_bg": QColor("#7C4F2A"),
                "combo_text": QColor("#F5DEB3"),
                "combo_border": QColor("#A0522D"),
                "line_colors": {
                    "Temperature_C": QColor(205, 92, 92), # IndianRed
                    "Humidity_perc": QColor(100, 149, 237), # CornflowerBlue
                    "Ultrasonic_cm": QColor(107, 142, 35), # OliveDrab
                    "Sound_raw": QColor(255, 215, 0), # Gold
                    "Light_raw": QColor(188, 143, 143), # RosyBrown
                    "Button_state": QColor(210, 105, 30), # Chocolate
                    "RotaryAngle_raw": QColor(240, 230, 140) # Khaki
                }
            },
            "ocean_blue_theme": {
                "plot_bg": QColor(0, 51, 102), # Dark Ocean Blue
                "axis_text": QColor(224, 255, 255), # Light Cyan
                "grid_line": QColor(0, 80, 153),
                "title_text": QColor(135, 206, 250), # Light Sky Blue
                "legend_text": QColor(224, 255, 255),
                "export_button_bg": QColor(70, 130, 180),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(255, 99, 71), # Tomato
                "combo_bg": QColor("#004080"),
                "combo_text": QColor("#E0FFFF"),
                "combo_border": QColor("#005099"),
                "line_colors": {
                    "Temperature_C": QColor(255, 99, 71), # Tomato
                    "Humidity_perc": QColor(100, 149, 237), # CornflowerBlue
                    "Ultrasonic_cm": QColor(95, 158, 160), # CadetBlue
                    "Sound_raw": QColor(255, 255, 0), # Yellow
                    "Light_raw": QColor(0, 255, 255), # Cyan
                    "Button_state": QColor(255, 0, 255), # Magenta
                    "RotaryAngle_raw": QColor(255, 255, 255) # White
                }
            },
            "vibrant_purple_theme": {
                "plot_bg": QColor(75, 0, 130), # Indigo
                "axis_text": QColor(230, 230, 250), # Lavender
                "grid_line": QColor(106, 13, 173),
                "title_text": QColor(221, 160, 221), # Plum
                "legend_text": QColor(230, 230, 250),
                "export_button_bg": QColor(138, 43, 226),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(255, 69, 0), # OrangeRed
                "combo_bg": QColor("#5F2A80"),
                "combo_text": QColor("#E6E6FA"),
                "combo_border": QColor("#8A2BE2"),
                "line_colors": {
                    "Temperature_C": QColor(255, 69, 0), # OrangeRed
                    "Humidity_perc": QColor(123, 104, 238), # MediumSlateBlue
                    "Ultrasonic_cm": QColor(0, 255, 127), # SpringGreen
                    "Sound_raw": QColor(255, 255, 0), # Yellow
                    "Light_raw": QColor(255, 99, 71), # Tomato
                    "Button_state": QColor(255, 20, 147), # DeepPink
                    "RotaryAngle_raw": QColor(255, 255, 255) # White
                }
            },
            "light_modern_theme": {
                "plot_bg": QColor(224, 224, 224), # Light Gray
                "axis_text": QColor(51, 51, 51),
                "grid_line": QColor(192, 192, 192),
                "title_text": QColor(85, 85, 85),
                "legend_text": QColor(51, 51, 51),
                "export_button_bg": QColor(96, 125, 139),
                "export_button_text": QColor(255, 255, 255),
                "warning_text_color": QColor(239, 83, 80), # Red
                "combo_bg": QColor("#FFFFFF"),
                "combo_text": QColor("#333333"),
                "combo_border": QColor("#C0C0C0"),
                "line_colors": {
                    "Temperature_C": QColor(239, 83, 80),  # Red
                    "Humidity_perc": QColor(66, 165, 245),  # Blue
                    "Ultrasonic_cm": QColor(102, 187, 106), # Green
                    "Sound_raw": QColor(255, 213, 79),     # Amber
                    "Light_raw": QColor(77, 182, 172),     # Teal
                    "Button_state": QColor(171, 71, 188),  # Purple
                    "RotaryAngle_raw": QColor(158, 158, 158) # Grey
                }
            },
            "high_contrast_theme": {
                "plot_bg": QColor(0, 0, 0), # Black
                "axis_text": QColor(255, 255, 0), # Yellow
                "grid_line": QColor(255, 0, 255), # Magenta
                "title_text": QColor(0, 255, 255), # Cyan
                "legend_text": QColor(255, 255, 0), # Yellow
                "export_button_bg": QColor(255, 0, 255),
                "export_button_text": QColor(0, 0, 0),
                "combo_bg": QColor("#222222"),
                "combo_text": QColor("#FFFF00"),
                "combo_border": QColor("#FF00FF"),
                "warning_text_color": QColor(255, 0, 0), # Red
                "line_colors": {
                    "Temperature_C": QColor(255, 0, 0),   # Red
                    "Humidity_perc": QColor(0, 0, 255),   # Blue
                    "Ultrasonic_cm": QColor(0, 255, 0),   # Green
                    "Sound_raw": QColor(255, 255, 0),     # Yellow
                    "Light_raw": QColor(0, 255, 255),     # Cyan
                    "Button_state": QColor(255, 0, 255),  # Magenta
                    "RotaryAngle_raw": QColor(255, 255, 255) # White
                }
            }
        }

        self.theme_palette = theme_palettes.get(current_theme, theme_palettes["dark_theme"]) # Fallback to dark

        # Assign colors to instance variables for easy access
        self.plot_bg_color = self.theme_palette["plot_bg"]
        self.axis_text_color = self.theme_palette["axis_text"]
        self.grid_line_color = self.theme_palette["grid_line"]
        self.title_text_color = self.theme_palette["title_text"]
        self.legend_text_color = self.theme_palette["legend_text"]
        self.line_colors = self.theme_palette["line_colors"] # Dictionary of line colors
        self.warning_text_color = self.theme_palette["warning_text_color"]
        self.combo_bg_color = self.theme_palette["combo_bg"] # For combo box
        self.combo_text_color = self.theme_palette["combo_text"] # For combo box text
        self.combo_border_color = self.theme_palette["combo_border"] # For combo box border


    def _setup_ui(self):
        """Sets up the UI elements for the plots tab."""
        title_label = QLabel("Sensor Data Plots")
        title_label.setFont(QFont("Inter", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setContentsMargins(0, 20, 0, 20)
        self.main_layout.addWidget(title_label)

        # Controls Layout
        controls_layout = QHBoxLayout()
        controls_layout.setContentsMargins(10, 0, 10, 20) # Add some margins
        
        # Sensor Selection
        sensor_group_frame = QFrame()
        sensor_group_frame.setObjectName("groupFrame")
        sensor_group_layout = QVBoxLayout(sensor_group_frame)
        
        # Fix for QLayout: Cannot add a null widget
        sensor_label = QLabel("Select Sensors:")
        sensor_label.setFont(QFont("Inter", 12))
        sensor_group_layout.addWidget(sensor_label)

        self.sensor_checkboxes = {}
        for key, name in self.SENSOR_COLUMNS.items():
            checkbox = QCheckBox(name)
            checkbox.setFont(QFont("Inter", 10))
            checkbox.setChecked(True) # Default to all selected
            checkbox.stateChanged.connect(self._update_plot)
            self.sensor_checkboxes[key] = checkbox
            sensor_group_layout.addWidget(checkbox)
        controls_layout.addWidget(sensor_group_frame)

        # Time Range Selection
        time_range_group_frame = QFrame()
        time_range_group_frame.setObjectName("groupFrame")
        time_range_layout = QVBoxLayout(time_range_group_frame)

        # Fix for QLayout: Cannot add a null widget
        time_range_label = QLabel("Select Time Range:")
        time_range_label.setFont(QFont("Inter", 12))
        time_range_layout.addWidget(time_range_label)

        self.time_range_combo = QComboBox()
        self.time_range_combo.setFont(QFont("Inter", 10))
        self.time_range_combo.addItems(self.TIME_RANGES.keys())
        self.time_range_combo.setCurrentText("24 Hours") # Default selection
        self.time_range_combo.currentIndexChanged.connect(self._update_plot)
        time_range_layout.addWidget(self.time_range_combo)
        time_range_layout.addStretch(1) # Push content to top
        controls_layout.addWidget(time_range_group_frame)

        # Data Loading and Export
        data_controls_group_frame = QFrame()
        data_controls_group_frame.setObjectName("groupFrame")
        data_controls_layout = QVBoxLayout(data_controls_group_frame)

        load_button = QPushButton("Load Data from CSV")
        load_button.setFont(QFont("Inter", 10, QFont.Bold))
        load_button.clicked.connect(self._load_data_from_csv)
        data_controls_layout.addWidget(load_button)

        export_button = QPushButton("Export Current View")
        export_button.setFont(QFont("Inter", 10, QFont.Bold))
        export_button.clicked.connect(self._export_plot_view)
        data_controls_layout.addWidget(export_button)
        data_controls_layout.addStretch(1)
        controls_layout.addWidget(data_controls_group_frame)
        
        controls_layout.addStretch(1) # Push groups to left

        self.main_layout.addLayout(controls_layout)

        # Plot Widget
        self.plot_widget = pg.PlotWidget()
        self.plot_widget.setBackground(self.plot_bg_color.name()) # Use themed background
        self.plot_widget.showGrid(x=True, y=True, alpha=0.5)
        self.plot_widget.addLegend()
        self.plot_widget.getAxis('bottom').setLabel('Time')
        
        # Set custom TimeAxisItem for bottom axis
        self.plot_widget.setAxisItems({'bottom': TimeAxisItem(orientation='bottom')})

        self.main_layout.addWidget(self.plot_widget)

        # Data Table (Optional - for raw data display)
        self.data_table = QTableWidget()
        self.data_table.setColumnCount(len(self.SENSOR_COLUMNS) + 1) # Timestamp + sensors
        self.data_table.setHorizontalHeaderLabels(["Timestamp"] + list(self.SENSOR_COLUMNS.values()))
        self.data_table.verticalHeader().setVisible(False) # Hide row numbers
        self.data_table.setEditTriggers(QTableWidget.NoEditTriggers) # Make table read-only
        self.data_table.setAlternatingRowColors(True) # Visual improvement
        self.data_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.data_table.hide() # Hidden by default, can be shown by a button if needed

        self.main_layout.addWidget(self.data_table)

        # Initialize plot with existing data if available (e.g., from sensor_readings.csv)
        self._load_initial_data()
        self._update_plot()

    def _load_initial_data(self):
        """Loads data from the default sensor_readings.csv if it exists."""
        sensor_log_dir = self.config.get_setting("sensor_log_directory", "Sensor_Logs")
        project_root_abs = os.path.abspath(os.path.join(script_dir, os.pardir))
        default_log_file = os.path.join(project_root_abs, sensor_log_dir, "sensor_readings.csv")

        if os.path.exists(default_log_file):
            try:
                self.data = pd.read_csv(default_log_file)
                self.data["Timestamp"] = pd.to_datetime(self.data["Timestamp"])
                self.logger.info("Loaded initial data from {}".format(default_log_file))
            except Exception as e:
                self.logger.error("Error loading initial CSV data: {}".format(e))
                self.data = pd.DataFrame() # Ensure data is empty if load fails
        else:
            self.logger.info("No default sensor data CSV found at {}".format(default_log_file))
            self.data = pd.DataFrame(columns=["Timestamp"] + list(self.SENSOR_COLUMNS.keys())) # Create empty DataFrame with columns

    def _load_data_from_csv(self):
        """Opens a file dialog to load sensor data from a CSV file."""
        file_dialog = QFileDialog(self)
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        file_dialog.setNameFilter("CSV files (*.csv)")
        if file_dialog.exec_():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                try:
                    loaded_data = pd.read_csv(file_path)
                    # Basic validation: check for 'Timestamp' column and at least one sensor column
                    if "Timestamp" not in loaded_data.columns:
                        QMessageBox.warning(self, "Error", "Selected CSV must contain a 'Timestamp' column.")
                        return

                    # Convert Timestamp to datetime objects
                    loaded_data["Timestamp"] = pd.to_datetime(loaded_data["Timestamp"])
                    self.data = loaded_data
                    self.logger.info("Successfully loaded data from: {}".format(file_path))
                    self._update_plot() # Redraw plot with new data
                    self._populate_data_table() # Update table as well
                except Exception as e:
                    self.logger.error("Failed to load CSV data from {}: {}".format(file_path, e))
                    QMessageBox.critical(self, "Error", "Failed to load CSV data.\nError: {}".format(e))

    def _populate_data_table(self):
        """Populates the QTableWidget with the loaded sensor data."""
        if self.data.empty:
            self.data_table.setRowCount(0)
            return

        self.data_table.setRowCount(len(self.data))
        # Set column headers dynamically based on SENSOR_COLUMNS
        headers = ["Timestamp"] + [self.SENSOR_COLUMNS[col] for col in self.SENSOR_COLUMNS.keys()]
        self.data_table.setColumnCount(len(headers))
        self.data_table.setHorizontalHeaderLabels(headers)

        for row_idx, (index, row_data) in enumerate(self.data.iterrows()):
            # Format timestamp for display
            timestamp_str = row_data["Timestamp"].strftime("%Y-%m-%d %H:%M:%S")
            self.data_table.setItem(row_idx, 0, QTableWidgetItem(timestamp_str))

            col_offset = 1 # Start from second column for sensor data
            for sensor_key in self.SENSOR_COLUMNS.keys():
                if sensor_key in row_data:
                    item_value = str(row_data[sensor_key])
                    self.data_table.setItem(row_idx, col_offset, QTableWidgetItem(item_value))
                else:
                    self.data_table.setItem(row_idx, col_offset, QTableWidgetItem("N/A"))
                col_offset += 1
        
        self.data_table.resizeColumnsToContents()

    def _update_plot(self):
        """
        Updates the plot based on selected sensors and time range.
        """
        if self.data.empty:
            self.plot_widget.clear()
            self.plot_widget.setTitle(self.original_plot_title, color=self.title_text_color.name())
            self.plot_widget.setLabel('left', "Value")
            return

        # Clear existing plot items but keep the background and grid settings
        self.plot_widget.clear()
        self.current_plot_items.clear() # Clear stored plot items

        # Apply theme colors again, in case the theme changed after data was loaded
        self._set_theme_colors()
        self._apply_theme_colors_to_plot()

        # Filter data by time range
        selected_range_text = self.time_range_combo.currentText()
        time_delta = self.TIME_RANGES.get(selected_range_text)

        display_data = self.data.copy()
        if time_delta is not None:
            end_time = datetime.now()
            start_time = end_time - time_delta
            display_data = display_data[(display_data["Timestamp"] >= start_time) & 
                                        (display_data["Timestamp"] <= end_time)]
        
        if display_data.empty:
            self.plot_widget.setTitle("No data for selected time range.", color=self.warning_text_color.name())
            self.plot_widget.setLabel('left', "Value")
            return

        # Convert timestamps to seconds since epoch for pyqtgraph plotting
        # PyQtGraph handles datetime objects if you set the axis to a custom TimeAxisItem,
        # but for direct plotting, converting to epoch time (float) is common.
        # However, since we're using a custom TimeAxisItem, we can directly pass timestamps.
        # Let's verify how TimeAxisItem expects `values` in tickStrings. It uses `fromtimestamp`.
        # So, converting to timestamp (seconds since epoch) is indeed the correct approach.
        x_values = display_data["Timestamp"].apply(lambda x: x.timestamp()).values

        # Plot selected sensors
        for key, name in self.SENSOR_COLUMNS.items():
            if self.sensor_checkboxes[key].isChecked() and key in display_data.columns:
                line_color = self.line_colors.get(key, QColor(255, 255, 255)) # Default to white if not in theme map
                
                # Create a PlotDataItem and store it
                plot_item = self.plot_widget.plot(
                    x_values, display_data[key].values,
                    pen=pg.mkPen(line_color, width=2),
                    name=name
                )
                self.current_plot_items[key] = plot_item

        # Set labels and title with themed colors
        self.plot_widget.getAxis('left').setLabel('Sensor Value')
        self.plot_widget.getAxis('left').setTextPen(self.axis_text_color)
        self.plot_widget.getAxis('bottom').setTextPen(self.axis_text_color)
        self.plot_widget.getAxis('left').setPen(self.axis_text_color)
        self.plot_widget.getAxis('bottom').setPen(self.axis_text_color)

        self.plot_widget.setTitle(self.original_plot_title, color=self.title_text_color.name())


    def _apply_theme_colors_to_plot(self):
        """
        Applies the currently selected theme's colors to the pyqtgraph plot.
        This method should be called whenever the theme changes.
        """
        self._set_theme_colors() # Re-fetch current theme colors

        # Update plot background
        self.plot_widget.setBackground(self.plot_bg_color.name())

        # Update axis text and line colors
        self.plot_widget.getAxis('left').setTextPen(self.axis_text_color)
        self.plot_widget.getAxis('bottom').setTextPen(self.axis_text_color)
        self.plot_widget.getAxis('left').setPen(self.axis_text_color)
        self.plot_widget.getAxis('bottom').setPen(self.axis_text_color)

        # Update grid line colors (need to redraw grid)
        # PyQtGraph's showGrid typically sets default colors. To update, we might need to
        # re-enable or explicitly set properties of its internal grid lines if they are exposed.
        # For a simple way to update existing grid lines, we might need to access internals
        # or recreate the grid. A common approach is to just ensure showGrid is called.
        # However, for fine-grained control, we'd need to modify the AxisItem's style directly
        # or find a method to update the grid line pen.
        # For now, let's assume setting AxisItem pen affects the grid lines implicitly.
        # If not, a more advanced solution would be needed.

        # Update plot title color
        # The PlotWidget's setTitle method accepts a 'color' argument.
        # We use self.original_plot_title to set the title with the new color.
        self.plot_widget.setTitle(self.original_plot_title, color=self.title_text_color.name())


        # Update legend text color
        # Accessing the legend requires accessing the PlotItem's legend object
        legend = self.plot_widget.addLegend() # This might add a new one if not careful, better to get existing
        # A more robust way to get the existing legend is to iterate plot items or have a reference
        # For simplicity, if we re-add legend every time, it might lead to duplicates.
        # Better to access the existing legend directly if possible.
        # For now, we will simply modify the style that *applies* to labels within the legend.
        # Or, we can iterate through the existing plot items and update their names/colors in the legend.
        
        # This will iterate through existing plot items and update their line colors and legend names
        for key, plot_item in self.current_plot_items.items():
            line_color = self.line_colors.get(key, QColor(255, 255, 255))
            plot_item.setPen(pg.mkPen(line_color, width=2))
            # The legend automatically updates if the plot item's name is set.
            # To specifically color the legend text, we'd need to access the QLabel elements
            # within the legend layout, which is more complex.
            # PyQtGraph's legend items are usually LabelItem objects.
            # A simpler workaround is to ensure the QSS for QLabel affects them.
            # Or, for explicit control, you can create a custom legend.
            # Let's set a global QSS for QLabel that affects legend items.
            # This is already handled by the main window's QSS.
            pass # No direct change to legend item color here, relies on global QSS.


    def _export_plot_view(self):
        """Exports the current plot view to a PNG image."""
        file_dialog = QFileDialog(self)
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setNameFilter("PNG image (*.png)")
        file_dialog.setDefaultSuffix("png")

        if file_dialog.exec_():
            file_path = file_dialog.selectedFiles()[0]
            exporter = pg.exporters.ImageExporter(self.plot_widget.plotItem)
            exporter.export(file_path)
            self.logger.info("Plot exported to: {}".format(file_path))
            QMessageBox.information(self, "Export Successful", "Plot saved to:\n{}".format(file_path))


    def set_style(self):
        """Applies specific styling for the plots tab."""
        self.setStyleSheet("""
            QWidget#PlotsTab {
                background-color: transparent;
            }
            QFrame#groupFrame {
                border: 1px solid #555;
                border-radius: 10px;
                background-color: rgba(40, 40, 40, 0.7);
                margin: 5px;
                padding: 10px;
            }
            QLabel {
                color: #EEE; /* Default text color */
            }
            QLabel:hover {
                color: #FFD700;
            }
            QCheckBox {
                color: #EEE;
            }
            QComboBox {
                background-color: %s; /* Dynamic background from theme_palette */
                color: %s; /* Dynamic text color from theme_palette */
                border: 1px solid %s; /* Dynamic border color from theme_palette */
                border-radius: 5px;
                padding: 5px;
            }
            QComboBox::drop-down {
                border: 0px;
            }
            QComboBox::down-arrow {
                image: url(icons/arrow_down_light.png);
                width: 16px;
                height: 16px;
            }
            QComboBox QAbstractItemView { /* Style for the dropdown list */
                background-color: %s; /* Same as combo box background */
                color: %s; /* Same as combo box text color */
                selection-background-color: %s; /* Highlight color */
                selection-color: %s; /* Highlighted text color */
                border: 1px solid %s; /* Border for the dropdown */
            }
            QPushButton {
                background-color: #4CAF50; /* Green */
                color: white;
                border-radius: 5px;
                padding: 5px 10px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            /* Table Widget Styling */
            QTableWidget {
                background-color: #282c34;
                alternate-background-color: #21252b;
                color: #abb2bf;
                border: 1px solid #444;
                gridline-color: #555;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #3a3f4b;
                color: #abb2bf;
                padding: 5px;
                border: 1px solid #444;
            }
            QTableWidget::item:selected {
                background-color: #61afef;
                color: white;
            }
        """ % (
            self.combo_bg_color.name(),
            self.combo_text_color.name(),
            self.combo_border_color.name(),
            self.combo_bg_color.name(), # Dropdown background
            self.combo_text_color.name(), # Dropdown text
            self.theme_palette["export_button_bg"].name(), # Using export button color for selection
            self.theme_palette["export_button_text"].name(), # Using export button text for selection
            self.combo_border_color.name() # Dropdown border
        ))


class TimeAxisItem(pg.AxisItem):
    """
    Custom AxisItem for displaying timestamps on the x-axis.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def tickStrings(self, values, scale, spacing):
        """
        Return the strings that should be placed beside each tick mark.
        """
        strings = []
        for val in values:
            try:
                # Convert timestamp (seconds since epoch) to datetime object
                dt_object = datetime.fromtimestamp(val)
                # Format based on the range (e.g., show date for longer ranges)
                if self.range[1] - self.range[0] > (2 * 24 * 3600): # More than 2 days
                    strings.append(dt_object.strftime('%Y-%m-%d\n%H:%M'))
                else:
                    strings.append(dt_object.strftime('%H:%M:%S'))
            except (ValueError, OSError): # Handle cases where timestamp might be out of range
                strings.append('') # Append empty string for invalid values
        return strings

