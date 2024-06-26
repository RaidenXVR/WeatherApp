import asyncio
import json
import logging
import time
import traceback

import pytz
import requests
from pyowm import OWM
import os
import dotenv as dv
from pyowm.weatherapi25.observation import Observation
from pyowm.weatherapi25.weather import Weather
from pyowm.utils import config
from datetime import datetime, timedelta
from plyer import gps
from plyer.utils import platform
if platform == "android":
    from android.storage import app_storage_path as app_path

def app_storage_path():
    if platform == "android":
        return app_path()+"/app"
    else:
        return "."
async def get_weather(lat: float, long: float):
    try:
        app_path = app_storage_path()
        logging.warning(os.listdir(app_path))
        dv.load_dotenv(dotenv_path=os.path.join(app_path, "tkowm"))
        tk = dv.get_key(os.path.join(app_path, "tkowm"), "WEATHER")

        owm = OWM(tk)
        manager = owm.weather_manager()

        observe: Observation = manager.weather_at_coords(lat, long)
        res = requests.get(
            url=f"https://pro.openweathermap.org/data/2.5/forecast/hourly?lat={lat}&lon={long}&appid={tk}&cnt=4&units=metric")

        forecast = res.json()["list"]
        current: Weather = observe.weather

        status = current.status
        detail = current.detailed_status
        temp = str(current.temperature('celsius').get("temp"))
        hum = str(current.humidity)
        wth = current.weather_icon_name
        uv = current.uvi
        wind = str(current.wind()["speed"])

        forecast_data = {}
        for item in forecast:
            time = utc_to_gmt_7(item["dt_txt"])
            time = str(time) + ".00"
            forecast_data[time] = {
                "temp": str(item['main']['temp']),
                "weather": item['weather'][0]["main"],
                "weather_desc": item['weather'][0]["description"],
                "icon": item['weather'][0]["icon"]

            }
        if uv is None:
            uv = "N/A"
        data = {"current": {"weather": status,
                            "weather_desc": detail,
                            "temp": temp,
                            "hum": hum,
                            "icon": wth,
                            "uv": uv,
                            "wind": wind
                            }
            , "forecast": forecast_data}

        return data

    except Exception as e:
        logging.warning("An error occurred: %s", str(e))
        return e


def utc_to_gmt_7(utc_time_str):
    time_format = "%Y-%m-%d %H:%M:%S"
    utc_time = datetime.strptime(utc_time_str, time_format)
    utc_time = utc_time.replace(tzinfo=pytz.utc)

    # Convert the datetime object to GMT+7 timezone
    gmt7_timezone = pytz.timezone('Asia/Bangkok')
    gmt7_time = utc_time.astimezone(gmt7_timezone)
    return gmt7_time.hour


async def get_location():
    gps_location = {}
    app_path = app_storage_path()

    def on_location(**kwargs):
        nonlocal gps_location
        gps_location = kwargs
    try:
        gps.configure(on_location=on_location)
        gps.start()

        await asyncio.sleep(3)

    except Exception as e:
        logging.error(e)
        return e

    finally:
        gps.stop()

    logging.warning(str(gps_location))

    lat = gps_location.get("lat")
    lon = gps_location.get("lon")
    logging.info(f"lat: {lat}, lon: {lon}")

    config_dict = config.get_default_config_for_subscription_type('developer')

    dv.load_dotenv(dotenv_path=os.path.join(app_path, "tkowm"))
    tk = dv.get_key(os.path.join(app_path, "tkowm"), "WEATHER")
    owm = OWM(api_key=tk, config=config_dict)
    manager = owm.weather_manager()

    observe: Observation = manager.weather_at_coords(lat, lon)
    logging.info(f"lat: {lat}, lon: {lon}")
    name: str = observe.location.name
    logging.info(f"city: {name}")
    with open(os.path.join(app_path, "cities.json"), "r") as c:
        cities_name = json.load(c)
    if name not in cities_name.keys():
        name2 = name.split(" ")
        if name2[0] in cities_name.keys():
            return name2[0], lat, lon
        else:
            raise Exception
    return name, lat, lon
