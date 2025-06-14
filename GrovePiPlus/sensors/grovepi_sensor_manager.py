# sensors/grovepi_sensor_manager.py
import os
import sys
import random
import time
from datetime import datetime
from PyQt5.QtCore import pyqtSignal, QObject

# Add SensorApp root to path to ensure utils can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.logger import Logger
from utils.config_manager import ConfigManager

# Conditional import of grovepi
try:
    import grovepi
    GROVEPI_AVAILABLE = True
except ImportError:
    GROVEPI_AVAILABLE = False
    print("WARNING: grovepi library not found. Running in MOCK mode only.")

class GrovePiSensorManager(QObject):
    """
    Manages all GrovePi+ sensor interactions, including reading values
    and controlling outputs. Supports mocking for development.
    """
    # Signals for interactive controls
    relay_status_changed = pyqtSignal(int) # 0 for off, 1 for on
    led_bar_status_changed = pyqtSignal(int) # 0-10 for segments lit

    def __init__(self, mock_sensors=False):
        super(GrovePiSensorManager, self).__init__()
        self.logger = Logger.get_logger()
        self.config = ConfigManager.get_instance()
        self.mock_sensors = mock_sensors or not GROVEPI_AVAILABLE

        # Sensor Definitions
        self.DHT_PORT = 2        # Digital Port 2
        self.BUTTON_PORT = 3     # Digital Port 3
        self.RELAY_PORT = 4      # Digital Port 4
        self.LED_BAR_PORT = 5    # Digital Port 5 (requires specific setup)
        self.ULTRASONIC_PORT = 7 # Digital Port 7

        self.ROTARY_ANGLE_PORT = 0 # Analog Port A0
        self.SOUND_PORT = 1      # Analog Port A1
        self.LIGHT_PORT = 2      # Analog Port A2

        # DHT Type (0 for DHT11, 1 for DHT22)
        self.DHT_TYPE = 0 

        # Current states for interactive controls
        self._relay_state = 0 # 0 = OFF, 1 = ON
        self._led_bar_level = 0 # 0-10

        self._setup_grovepi_pins()
        self._setup_logging_files()

        if self.mock_sensors:
            self.logger.info("GrovePiSensorManager initialized in MOCK SENSORS mode.")
        else:
            self.logger.info("GrovePiSensorManager initialized with physical GrovePi.")

    def _setup_grovepi_pins(self):
        """
        Sets up the GrovePi pins based on their type (input/output).
        Only executed if not in mock mode.
        """
        if self.mock_sensors:
            return

        try:
            # Set digital ports as input/output
            grovepi.pinMode(self.BUTTON_PORT, "INPUT")
            grovepi.pinMode(self.RELAY_PORT, "OUTPUT")
            grovepi.pinMode(self.LED_BAR_PORT, "OUTPUT") # LED Bar needs to be set as OUTPUT
            
            # Initialize relay and LED bar to known states
            grovepi.digitalWrite(self.RELAY_PORT, 0)
            self._relay_state = 0
            self.relay_status_changed.emit(self._relay_state)

            # LED bar setup (special case, not a simple digitalWrite)
            # For LED bar, usually you write to a specific register or use a library function
            # Since the user specified "Grovepi Library provided by Dexter",
            # we'll assume `grovepi.setLedBarLevel()` or similar exists.
            # If not, direct digital writes to specific pins of the LED bar module would be needed,
            # which is more complex and usually handled by a higher-level function.
            # For this example, we will assume `grovepi.ledBar_SetLevel(pin, level)` exists.
            # If it doesn't, this part will need adjustment based on Dexter's actual API.
            # A common library function is `grovepi.ledBar_setLevel(pin, level)`.
            # Let's assume it exists and handles the output.
            if hasattr(grovepi, 'ledBar_init') and hasattr(grovepi, 'ledBar_setLevel'):
                 grovepi.ledBar_init(self.LED_BAR_PORT, 0) # Initialize LED bar on D5, style 0
                 grovepi.ledBar_setLevel(self.LED_BAR_PORT, 0)
            elif hasattr(grovepi, 'setLedBarLevel'): # Less common, but sometimes used in examples
                 grovepi.setLedBarLevel(self.LED_BAR_PORT, 0)
            else:
                self.logger.warning("LED Bar function `ledBar_setLevel` or `setLedBarLevel` not found in grovepi. "
                                    "LED Bar control might not work as expected.")
                self.mock_sensors = True # Fallback to mock for LED Bar if specific function missing
            self._led_bar_level = 0
            self.led_bar_status_changed.emit(self._led_bar_level)

            self.logger.info("GrovePi pins initialized.")
        except Exception as e:
            self.logger.error("Error setting up GrovePi pins: {}. Falling back to MOCK mode.".format(e))
            self.mock_sensors = True # Fallback to mock if setup fails

    def _setup_logging_files(self):
        """
        Ensures the sensor log directory and file exist.
        """
        self.sensor_log_dir = self.config.get_setting("sensor_log_directory", "Sensor_Logs")
        self.sensor_log_file = os.path.join(self.sensor_log_dir, "sensor_readings.csv")

        # Resolve to absolute path relative to project root
        project_root_abs = os.path.abspath(os.path.join(script_dir, os.pardir))
        full_sensor_log_dir_path = os.path.join(project_root_abs, self.sensor_log_dir)
        self.sensor_log_file = os.path.join(full_sensor_log_dir_path, "sensor_readings.csv")


        if not os.path.exists(full_sensor_log_dir_path):
            os.makedirs(full_sensor_log_dir_path)
            self.logger.info("Created sensor log directory: {}".format(full_sensor_log_dir_path))

        if not os.path.exists(self.sensor_log_file):
            with open(self.sensor_log_file, 'w') as f:
                f.write("Timestamp,Temperature_C,Humidity_perc,Ultrasonic_cm,Sound_raw,Light_raw,Button_state,RotaryAngle_raw\n")
            self.logger.info("Created sensor log file: {}".format(self.sensor_log_file))

    def log_sensor_data(self, data):
        """
        Logs sensor data to a CSV file.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            line = "{},{},{},{},{},{},{},{}\n".format(
                timestamp,
                data.get("temperature", ""),
                data.get("humidity", ""),
                data.get("ultrasonic", ""),
                data.get("sound", ""),
                data.get("light", ""),
                data.get("button", ""),
                data.get("rotary_angle", "")
            )
            with open(self.sensor_log_file, 'a') as f:
                f.write(line)
        except Exception as e:
            self.logger.error("Error writing sensor data to CSV: {}".format(e))

    # --- Sensor Reading Functions ---

    def read_dht_sensor(self):
        """Reads temperature and humidity from DHT sensor on D2."""
        if self.mock_sensors:
            temp = random.uniform(18.0, 30.0)
            hum = random.uniform(40.0, 90.0)
            return temp, hum
        try:
            [temp, hum] = grovepi.dht(self.DHT_PORT, self.DHT_TYPE)
            if not isinstance(temp, float) or not isinstance(hum, float):
                # Sometimes GrovePi returns 'nan' or non-float values on initial reads or errors
                raise ValueError("Invalid DHT sensor reading: {} {}".format(temp, hum))
            return temp, hum
        except Exception as e:
            self.logger.error("Error reading DHT sensor (D{}): {}".format(self.DHT_PORT, e))
            return 0.0, 0.0

    def read_button_sensor(self):
        """Reads button state (0 or 1) from D3."""
        if self.mock_sensors:
            return random.choice([0, 1]) # Simulate button press/release
        try:
            return grovepi.digitalRead(self.BUTTON_PORT)
        except Exception as e:
            self.logger.error("Error reading Button sensor (D{}): {}".format(self.BUTTON_PORT, e))
            return 0

    def read_ultrasonic_sensor(self):
        """Reads distance from Ultrasonic sensor on D7."""
        if self.mock_sensors:
            return random.uniform(5.0, 200.0)
        try:
            return grovepi.ultrasonicRead(self.ULTRASONIC_PORT)
        except Exception as e:
            self.logger.error("Error reading Ultrasonic sensor (D{}): {}".format(self.ULTRASONIC_PORT, e))
            return 0.0

    def read_rotary_angle_sensor(self):
        """Reads raw analog value from Rotary Angle sensor on A0 (0-1023)."""
        if self.mock_sensors:
            return random.randint(0, 1023)
        try:
            return grovepi.analogRead(self.ROTARY_ANGLE_PORT)
        except Exception as e:
            self.logger.error("Error reading Rotary Angle sensor (A{}): {}".format(self.ROTARY_ANGLE_PORT, e))
            return 0

    def read_sound_sensor(self):
        """Reads raw analog value from Sound sensor on A1 (0-1023)."""
        if self.mock_sensors:
            return random.randint(0, 1023)
        try:
            return grovepi.analogRead(self.SOUND_PORT)
        except Exception as e:
            self.logger.error("Error reading Sound sensor (A{}): {}".format(self.SOUND_PORT, e))
            return 0

    def read_light_sensor(self):
        """Reads raw analog value from Light sensor on A2 (0-1023)."""
        if self.mock_sensors:
            return random.randint(0, 1023)
        try:
            return grovepi.analogRead(self.LIGHT_PORT)
        except Exception as e:
            self.logger.error("Error reading Light sensor (A{}): {}".format(self.LIGHT_PORT, e))
            return 0

    # --- Sensor Control Functions ---

    def control_relay(self, state):
        """Controls the Relay on D4 (0 for OFF, 1 for ON)."""
        new_state = 1 if state else 0
        if self._relay_state == new_state:
            return # No change needed

        if self.mock_sensors:
            self.logger.info("MOCK: Setting Relay (D{}) to {}".format(self.RELAY_PORT, "ON" if new_state else "OFF"))
            self._relay_state = new_state
            self.relay_status_changed.emit(self._relay_state)
            return

        try:
            grovepi.digitalWrite(self.RELAY_PORT, new_state)
            self._relay_state = new_state
            self.relay_status_changed.emit(self._relay_state)
            self.logger.info("Set Relay (D{}) to {}".format(self.RELAY_PORT, "ON" if new_state else "OFF"))
        except Exception as e:
            self.logger.error("Error controlling Relay (D{}): {}".format(self.RELAY_PORT, e))

    def control_led_bar(self, level):
        """Controls the LED Bar on D5 (0-10 segments lit)."""
        new_level = int(max(0, min(10, level))) # Clamp level between 0 and 10
        if self._led_bar_level == new_level:
            return # No change needed

        if self.mock_sensors:
            self.logger.info("MOCK: Setting LED Bar (D{}) level to {}".format(self.LED_BAR_PORT, new_level))
            self._led_bar_level = new_level
            self.led_bar_status_changed.emit(self._led_bar_level)
            return

        try:
            # Assuming grovepi.ledBar_setLevel(pin, level) is available
            if hasattr(grovepi, 'ledBar_setLevel'):
                grovepi.ledBar_setLevel(self.LED_BAR_PORT, new_level)
                self._led_bar_level = new_level
                self.led_bar_status_changed.emit(self._led_bar_level)
                self.logger.info("Set LED Bar (D{}) level to {}".format(self.LED_BAR_PORT, new_level))
            else:
                self.logger.warning("LED Bar function `ledBar_setLevel` not found in grovepi. Cannot control actual LED Bar.")
                self.mock_sensors = True # Fallback if function missing
        except Exception as e:
            self.logger.error("Error controlling LED Bar (D{}): {}".format(self.LED_BAR_PORT, e))

