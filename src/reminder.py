import sqlite3
import datetime
from telegram import Bot

DATABASE = 'reminders.db'


def initialize_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 reminder_time TIMESTAMP,
                 message TEXT)''')
    conn.commit()
    conn.close()


initialize_database()


def add_reminder(time_str, message):
    try:
        reminder_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    except ValueError:
        raise ValueError(
            'неправильный формат времени. Используйте формат: YYYY-MM-DD HH:MM')

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('INSERT INTO reminders (reminder_time, message) VALUES (?, ?)',
              (reminder_time, message))
    conn.commit()
    conn.close()


def list_reminders():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT * FROM reminders ORDER BY reminder_time')
    reminders = c.fetchall()
    conn.close()
    return reminders


def delete_reminder_by_index(index):
    reminders = list_reminders()
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
