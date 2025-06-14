# utils/weather_api.py
import os
import sys
import json
import time

# Add SensorApp root to path to ensure utils can be imported
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, os.pardir))
if project_root not in sys.path:
    sys.path.append(project_root)

from utils.logger import Logger
from utils.config_manager import ConfigManager

# Python 3.5 doesn't have `requests` built-in, and installing it on RPi
# might require specific steps. For simplicity and built-in compatibility,
# we'll use `urllib.request` for HTTP requests.
# Note: urllib.request has a simpler API than requests.
try:
    # Python 3
    import urllib.request
    import urllib.parse
except ImportError:
    # Python 2 (though user specified Python 3.5)
    import urllib2 as urllib_request
    import urllib as urllib_parse


class WeatherAPI:
    """
    Fetches weather data from OpenWeatherMap API.
    """
    BASE_URL = "http://api.openweathermap.org/data/2.5/"

    def __init__(self):
        self.logger = Logger.get_logger()
        self.config = ConfigManager.get_instance()
        self._api_key = self.config.get_setting("openweathermap_api_key", "")

    def _make_request(self, endpoint, params):
        """
        Internal helper to make an HTTP GET request to the OpenWeatherMap API.
        """
        if not self._api_key:
            self.logger.warning("OpenWeatherMap API Key is not set in settings. Weather data will not be fetched.")
            return None

        params["appid"] = self._api_key
        params["units"] = "metric" # or "imperial" for Fahrenheit
        
        url_params = urllib.parse.urlencode(params)
        full_url = self.BASE_URL + endpoint + "?" + url_params
        
        try:
            self.logger.debug("Fetching weather from: {}".format(full_url))
            req = urllib.request.Request(full_url)
            with urllib.request.urlopen(req, timeout=10) as response:
                if response.getcode() == 200:
                    data = response.read().decode('utf-8')
                    return json.loads(data)
                else:
                    self.logger.error("Weather API request failed with status {}: {}".format(response.getcode(), response.read().decode('utf-8')))
                    return None
        except urllib.error.URLError as e:
            self.logger.error("Network error fetching weather data: {}".format(e.reason))
            return None
        except Exception as e:
            self.logger.error("An unexpected error occurred during weather API request: {}".format(e))
            return None

    def get_current_weather(self, city, country_code):
        """
        Fetches current weather data.
        :param city: City name.
        :param country_code: 2-letter country code (e.g., 'US', 'GB').
        :return: Dict of current weather data or None.
        """
        params = {
            "q": "{},{}".format(city, country_code)
        }
        data = self._make_request("weather", params)
        if data and "main" in data and "weather" in data:
            return {
                "description": data["weather"][0]["description"],
                "icon": data["weather"][0]["icon"],
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "humidity": data["main"]["humidity"],
                "pressure": data["main"]["pressure"],
                "wind_speed": data["wind"]["speed"] if "wind" in data else 0,
                "city_name": data["name"]
            }
        return None

    def get_forecast(self, city, country_code):
        """
        Fetches 5-day / 3-hour forecast data (which can be used for 24-hour forecast too).
        OpenWeatherMap's 'forecast' endpoint provides data every 3 hours.
        :param city: City name.
        :param country_code: 2-letter country code.
        :return: List of forecast dicts or None.
        """
        params = {
            "q": "{},{}".format(city, country_code)
        }
        data = self._make_request("forecast", params)
        if data and "list" in data:
            forecasts = []
            for item in data["list"]:
                forecasts.append({
                    "dt_txt": item["dt_txt"], # Date and time in "YYYY-MM-DD HH:MM:SS" format
                    "temperature": item["main"]["temp"],
                    "feels_like": item["main"]["feels_like"],
                    "description": item["weather"][0]["description"],
                    "icon": item["weather"][0]["icon"],
                    "humidity": item["main"]["humidity"],
                    "wind_speed": item["wind"]["speed"] if "wind" in item else 0
                })
            return forecasts
        return None

# Example usage (for testing)
if __name__ == "__main__":
    Logger.initialize(debug_to_console=True)
    # Set a dummy API key for testing. Replace with your actual key.
    ConfigManager.get_instance().set_setting("openweathermap_api_key", "YOUR_OPENWEATHERMAP_API_KEY") 
    api_key = ConfigManager.get_instance().get_setting("openweathermap_api_key")

    if api_key == "YOUR_OPENWEATHERMAP_API_KEY" or not api_key:
        print("Please set your OpenWeatherMap API key in utils/config_manager.py or app_config.json to test weather functionality.")
    else:
        weather_api = WeatherAPI()
        city = "Frisco"
        country = "US"

        print("--- Current Weather ---")
        current = weather_api.get_current_weather(city, country)
        if current:
            print("City: {}".format(current["city_name"]))
            print("Temp: {:.1f} C, Feels Like: {:.1f} C".format(current["temperature"], current["feels_like"]))
            print("Description: {}".format(current["description"]))
            print("Humidity: {}%".format(current["humidity"]))
        else:
            print("Failed to get current weather.")

        print("\n--- 5-Day / 24-Hour Forecast ---")
        forecasts = weather_api.get_forecast(city, country)
        if forecasts:
            # Display first 8 entries for a rough 24-hour forecast (8 * 3 hours = 24 hours)
            print("Next 24 hours (approx):")
            for i, fc in enumerate(forecasts[:8]):
                print("  {} - {:.1f} C, {}".format(fc["dt_txt"], fc["temperature"], fc["description"]))
            
            # Display daily forecast for 5 days (e.g., one entry per day at noon)
            print("\n5-Day Forecast (approx):")
            daily_forecast = {}
            for fc in forecasts:
                date = fc["dt_txt"].split(" ")[0]
                hour = int(fc["dt_txt"].split(" ")[1].split(":")[0])
                if date not in daily_forecast and hour >= 12 and hour <= 15: # Try to get a mid-day reading
                    daily_forecast[date] = fc
            
            for date_key in sorted(daily_forecast.keys())[:5]: # Show 5 days
                fc = daily_forecast[date_key]
                print("  {} - {:.1f} C, {}".format(date_key, fc["temperature"], fc["description"]))

        else:
            print("Failed to get forecast.")
