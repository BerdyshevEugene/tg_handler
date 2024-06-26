import sqlite3
import datetime

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


def delete_reminder(reminder_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()
    return c.rowcount > 0
