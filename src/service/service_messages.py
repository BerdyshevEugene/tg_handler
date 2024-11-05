import os
import sqlite3

from dotenv import load_dotenv
from loguru import logger
from telegram import Bot

DATABASE = 'reminders.db'

load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
bot = Bot(token=TG_BOT_TOKEN)


def get_all_users():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT DISTINCT user_id FROM reminders')
    users = c.fetchall()
    conn.close()
    return [user[0] for user in users]


async def send_service_message(message):
    users = get_all_users()
    for user_id in users:
        try:
            await bot.send_message(chat_id=user_id, text=message)
        except Exception as e:
            logger.error(f'failed to send message to user {user_id}: {e}')
