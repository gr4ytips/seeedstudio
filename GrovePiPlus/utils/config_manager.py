# utils/config_manager.py
import os
import json

class ConfigManager:
    """
    Manages application configuration settings, allowing persistence
    to a JSON file. Implements a Singleton pattern.
    """
    _instance = None
    _config_file_name = "app_config.json"
    _config_file_path = None # Will be set dynamically

    @staticmethod
    def get_instance():
        """
        Returns the singleton instance of ConfigManager.
        Initializes it if it doesn't exist.
        """
        if ConfigManager._instance is None:
            ConfigManager._instance = ConfigManager()
        return ConfigManager._instance

    def __init__(self):
        """
        Private constructor. Initializes config from file or defaults.
        """
        if ConfigManager._instance is not None:
            raise Exception("This class is a singleton! Use ConfigManager.get_instance()")
        
        # Determine config file path relative to the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
        ConfigManager._config_file_path = os.path.join(project_root, ConfigManager._config_file_name)

        self.config = {}
        self._load_config()

        # Set default settings if not present
        self._set_defaults()

    def _load_config(self):
        """Loads configuration from the JSON file."""
        if os.path.exists(ConfigManager._config_file_path):
            try:
                with open(ConfigManager._config_file_path, 'r') as f:
                    self.config = json.load(f)
            except Exception as e:
                # Log this error if logger is available, otherwise print
                print("WARNING: Could not load config file {}: {}".format(ConfigManager._config_file_path, e))
                self.config = {} # Reset to empty if loading fails
        else:
            self.config = {}

    def _save_config(self):
        """Saves current configuration to the JSON file."""
        try:
            with open(ConfigManager._config_file_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print("ERROR: Could not save config file {}: {}".format(ConfigManager._config_file_path, e))

    def _set_defaults(self):
        """Sets default values for configuration if they don't exist."""
        # General app settings
        self.config.setdefault("current_theme", "dark_theme")
        self.config.setdefault("sensor_read_interval", 2) # seconds
        self.config.setdefault("enable_mock_sensors", True) # New setting for mock mode

        # Logging settings
        self.config.setdefault("enable_debug_to_console", True)
        self.config.setdefault("enable_debug_to_file", True)
        self.config.setdefault("log_directory", "Debug_Logs") # Relative to app root
        self.config.setdefault("sensor_log_directory", "Sensor_Logs") # Relative to app root

        # Archiving settings
        self.config.setdefault("enable_archive", True)
        self.config.setdefault("archive_directory", "Archive_Sensor_Logs") # Relative to app root

        # Weather API settings
        self.config.setdefault("openweathermap_api_key", "") # User needs to set this
        self.config.setdefault("weather_city", "Frisco")
        self.config.setdefault("weather_country_code", "US")

        # Storage monitoring settings
        self.config.setdefault("min_free_space_gb", 0.5) # Minimum free space before warning (GB)
        self.config.setdefault("system_check_interval_ms", 60000) # How often to check system status (ms)

        # Save defaults immediately if they were just set (i.e., new file)
        if not os.path.exists(ConfigManager._config_file_path):
            self._save_config()

    def get_setting(self, key, default=None):
        """
        Retrieves a setting by its key.
        :param key: The key of the setting.
        :param default: The default value to return if the key is not found.
        :return: The setting value or the default.
        """
        return self.config.get(key, default)

    def set_setting(self, key, value):
        """
        Sets a configuration setting and saves it.
        :param key: The key of the setting.
        :param value: The new value for the setting.
        """
        self.config[key] = value
        self._save_config()

# Example usage (for testing purposes, will be implicitly used by app)
if __name__ == "__main__":
    config = ConfigManager.get_instance()
    
    print("Initial Theme:", config.get_setting("current_theme"))
    print("API Key:", config.get_setting("openweathermap_api_key"))

    config.set_setting("current_theme", "light_theme")
    config.set_setting("openweathermap_api_key", "your_api_key_123")
    config.set_setting("new_setting", "hello")

    print("New Theme:", config.get_setting("current_theme"))
    print("New API Key:", config.get_setting("openweathermap_api_key"))
    print("New Setting:", config.get_setting("new_setting"))

    # Verify persistence by creating a new instance (which will load from file)
    del ConfigManager._instance # Simulate restarting the app
    new_config_instance = ConfigManager.get_instance()
    print("After restart (simulated), Theme:", new_config_instance.get_setting("current_theme"))
    print("After restart (simulated), API Key:", new_config_instance.get_setting("openweathermap_api_key"))
    print("After restart (simulated), New Setting:", new_config_instance.get_setting("new_setting"))

    # Clean up test config file (optional)
    # if os.path.exists(ConfigManager._config_file_path):
    #     os.remove(ConfigManager._config_file_path)
