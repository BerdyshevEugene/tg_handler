import os
from dotenv import load_dotenv
from telegram import Bot
from pyowm import OWM
from pyowm.utils.config import get_default_config
from location_storage import get_all_locations


load_dotenv()

owm_api_key = os.getenv('OWM_API')
owm_config = get_default_config()
owm_config['language'] = 'ru'
owm = OWM(owm_api_key, owm_config)
mgr = owm.weather_manager()
chat_id = os.getenv('GROUP_ID')


def get_weather_text(city: str):
    observation = mgr.weather_at_place(city)
    w = observation.weather
    weather_text = f'Погода в городе {city}: {w.detailed_status}\nТемпература: {w.temperature("celsius")["temp"]}°C'
    if 'rain' in w.status.lower():
        weather_text += '\nВозьмите зонт, возможен дождь!'
    return weather_text


async def send_weather(bot, chat_id):
    locations = get_all_locations()
    for user_id, latitude, longitude in locations:
        observation = mgr.weather_at_coords(latitude, longitude)
        city = observation.location.name
        weather_text = get_weather_text(city)
        await bot.send_message(chat_id=chat_id, text=f'Пользователь {user_id}: {weather_text}')
