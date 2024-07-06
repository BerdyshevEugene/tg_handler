import sqlite3
import datetime

from loguru import logger

DATABASE = 'reminders.db'


def initialize_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 reminder_time TIMESTAMP,
                 message TEXT)''')
    conn.commit()
    conn.close()


initialize_database()


def add_reminder(user_id, time_str, message):
    try:
        reminder_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    except ValueError as e:
        error_message = 'неправильный формат времени. Используйте формат: YYYY-MM-DD HH:MM'
        logger.error(
            f'Failed to add reminder for user {user_id}: {error_message}. Error: {str(e)}')
        raise ValueError(error_message)

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO reminders (user_id, reminder_time, message) VALUES (?, ?, ?)',
              (user_id, reminder_time, message))
    conn.commit()
    conn.close()


def list_reminders(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        'SELECT * FROM reminders WHERE user_id=? ORDER BY reminder_time', (user_id,))
    reminders = c.fetchall()
    conn.close()
    return reminders


def delete_reminder_by_index(user_id, index):
    reminders = list_reminders(user_id)
    if index < 0 or index >= len(reminders):
        return False
    reminder_id = reminders[index][0]
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0


async def daily_summary(bot, chat_id):
    current_date = datetime.date.today()
    tomorrow_date = current_date + datetime.timedelta(days=1)
    reminders = list_reminders()

    tasks_today = [
        f'{i + 1}. {datetime.datetime.strptime(reminder[1], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")} {reminder[2]}'
        for i, reminder in enumerate(reminders)
        if datetime.datetime.strptime(reminder[1], '%Y-%m-%d %H:%M:%S').date() == current_date
    ]

    tasks_tomorrow = [
        f'{i + 1}. {datetime.datetime.strptime(reminder[1], "%Y-%m-%d %H:%M:%S").strftime("%H:%M")} {reminder[2]}'
        for i, reminder in enumerate(reminders)
        if datetime.datetime.strptime(reminder[1], '%Y-%m-%d %H:%M:%S').date() == tomorrow_date
    ]

    message = f'привет!\nежедневная сводка задач на сегодня, {current_date}:\n'
    if tasks_today:
        message += '\n'.join(tasks_today)
    else:
        message += 'на сегодня задач нет\n'

    message += f'\n\nзапланировано на завтра, {tomorrow_date}:\n'
    if tasks_tomorrow:
        message += '\n'.join(tasks_tomorrow)
    else:
        message += '\nна завтра задач нет'

    await bot.send_message(chat_id=chat_id, text=message)
