import asyncio
import json
import os
import sqlite3

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from pathlib import Path
from pyowm import OWM
from pyowm.utils.config import get_default_config
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

from reminder import add_reminder, list_reminders, delete_reminder
from location_storage import add_location, get_location, get_all_locations


# Загрузка переменных окружения
load_dotenv()
OWM_API = os.getenv('OWM_API')
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
CHANNEL_ID = os.getenv('CHANNEL_ID')
GROUP_ID = os.getenv('GROUP_ID')

# Конфигурация OpenWeatherMap
owm_api_key = OWM_API
owm_config = get_default_config()
owm_config['language'] = 'ru'

# Инициализация OWM
owm = OWM(owm_api_key, owm_config)
mgr = owm.weather_manager()

# Инициализация бота Telegram
bot_token = TG_BOT_TOKEN
channel_id = CHANNEL_ID
chat_id = GROUP_ID
bot = Bot(token=bot_token)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_list = [
        '/start - Начать взаимодействие с ботом',
        '/addreminder YYYY-MM-DD HH:MM ваше_сообщение - Добавить напоминание',
        '/listreminders - Показать список текущих напоминаний',
        '/deletereminder номер - Удалить напоминание по номеру',
        '/sendlocation - Отправьте ваше местоположение, чтобы получать прогноз погоды'
    ]
    await update.message.reply_text('Привет! Список команд:\n' + '\n'.join(commands_list))


async def sendlocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Пожалуйста, отправьте мне ваше местоположение, чтобы я мог отправлять вам прогноз погоды.'
    )


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_location = update.message.location
    add_location(user_id, user_location.latitude, user_location.longitude)
    await update.message.reply_text(
        'Местоположение сохранено! Теперь я буду отправлять вам прогноз погоды.'
    )


def get_weather_text(city: str):
    observation = mgr.weather_at_place(city)
    w = observation.weather
    weather_text = f'Погода в городе {city}: {w.detailed_status}\nТемпература: {w.temperature("celsius")["temp"]}°C'
    if 'rain' in w.status.lower():
        weather_text += '\nВозьмите зонт, возможен дождь!'
    return weather_text


async def send_weather():
    locations = get_all_locations()
    for user_id, latitude, longitude in locations:
        observation = mgr.weather_at_coords(latitude, longitude)
        city = observation.location.name
        weather_text = get_weather_text(city)
        await bot.send_message(chat_id=chat_id, text=f'Пользователь {user_id}: {weather_text}')


async def list_user_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_list = [
        '/start - начать взаимодействие с ботом',
        '/addreminder YYYY-MM-DD HH:MM <ваше_сообщение> - добавить напоминание',
        '/listreminders - отобразить список текущих напоминаний',
        '/deletereminder <номер> - удалить напоминание по номеру'
    ]
    await update.message.reply_text('\n'.join(commands_list))


async def handle_add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time_str = context.args[0] + ' ' + context.args[1]
        message = ' '.join(context.args[2:])
        add_reminder(time_str, message)
        await update.message.reply_text('напоминание добавлено')
    except (IndexError, ValueError):
        await update.message.reply_text('неправильный формат. Используйте: /addreminder YYYY-MM-DD HH:MM <ваше_сообщение>')


async def handle_list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminders = list_reminders()
    reminder_texts = [
        f'{i + 1}. {reminder[1]}: {reminder[2]}' for i, reminder in enumerate(reminders)]
    if reminder_texts:
        await update.message.reply_text('\n'.join(reminder_texts))
    else:
        await update.message.reply_text('напоминаний нет')


async def handle_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reminder_id = int(context.args[0])
        if delete_reminder(reminder_id):
            await update.message.reply_text('напоминание удалено')
        else:
            await update.message.reply_text('напоминания с таким номером не найдено')
    except (IndexError, ValueError):
        await update.message.reply_text('неправильный формат. Используйте: /deletereminder <номер>')


if __name__ == '__main__':
    application = Application.builder().token(bot_token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(MessageHandler(filters.LOCATION, location))
    application.add_handler(CommandHandler('listcommands', list_user_commands))
    application.add_handler(CommandHandler('addreminder', handle_add_reminder))
    application.add_handler(CommandHandler(
        'listreminders', handle_list_reminders))
    application.add_handler(CommandHandler(
        'deletereminder', handle_delete_reminder))

    # cоздаем планировщик и добавляем задачу
    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_weather, 'interval', hours=3)
    scheduler.start()

    # запуск бота
    application.run_polling()
