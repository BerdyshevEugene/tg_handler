import os
import pytz

from dotenv import load_dotenv
from loguru import logger
from telegram import Bot
from tenacity import retry, wait_fixed, stop_after_attempt
from pyowm import OWM
from pyowm.utils.config import get_default_config
from pyowm.utils import timestamps
from datetime import datetime, timedelta

load_dotenv()

owm_api_key = os.getenv('OWM_API')
owm = OWM(owm_api_key)
mgr = owm.weather_manager()
config_dict = get_default_config()
config_dict['language'] = 'ru'

weather_icons = {
    'Clear': '☀️',
    'Clouds': '☁️',
    'Rain': '🌧',
    'Drizzle': '🌦',
    'Thunderstorm': '⛈',
    'Snow': '❄️',
    'Mist': '🌫',
    'Fog': '🌫',
    'Haze': '🌫',
    'Smoke': '🌫'
}


def get_weather_icon(status):
    return weather_icons.get(status, '')


@retry(wait=wait_fixed(2), stop=stop_after_attempt(3))
def get_weather_forecast(lat, lon):
    observation = mgr.weather_at_coords(lat, lon)
    weather = observation.weather
    status = weather.detailed_status
    temperature = weather.temperature('celsius')['temp']
    icon = get_weather_icon(weather.status)
    return f'{icon} {status.capitalize()}, температура: {temperature}°C'


async def send_weather(bot: Bot, user_id: int, chat_id: int, latitude: float, longitude: float):
    try:
        weather_forecast = get_weather_forecast(latitude, longitude)
        message = f'Погода сейчас:\n{weather_forecast}'
        await bot.send_message(chat_id=chat_id, text=message)
        logger.info(
            f'the weather report has been sent to the user {user_id}')
    except Exception as e:
        logger.error(
            f'failed to send a message to the user {user_id}: {e}')
