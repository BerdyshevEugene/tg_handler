import sqlite3
from datetime import datetime

DB_REMINDERS = 'reminders.db'
DB_LOCATIONS = 'locations.db'


def initialize_reminder_db():
    with sqlite3.connect(DB_REMINDERS) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS reminders
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                     user_id INTEGER,
                     reminder_time TIMESTAMP,
                     message TEXT)''')
        conn.commit()

        required_columns = {'user_id': 'INTEGER',
                            'reminder_time': 'TIMESTAMP', 'message': 'TEXT'}
        existing_columns = {column[1] for column in c.execute(
            'PRAGMA table_info(reminders)')}

        for col, col_type in required_columns.items():
            if col not in existing_columns:
                c.execute(f'ALTER TABLE reminders ADD COLUMN {col} {col_type}')
        conn.commit()


def initialize_location_db():
    with sqlite3.connect(DB_LOCATIONS) as conn:
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS locations
                     (user_id INTEGER PRIMARY KEY,
                     latitude REAL,
                     longitude REAL,
                     chat_id INTEGER,
                     timezone TEXT,
                     hour INTEGER,
                     minute INTEGER)''')
        conn.commit()

        required_columns = {'latitude': 'REAL', 'longitude': 'REAL', 'chat_id': 'INTEGER',
                            'timezone': 'TEXT', 'hour': 'INTEGER', 'minute': 'INTEGER'}
        existing_columns = {column[1] for column in c.execute(
            'PRAGMA table_info(locations)')}

        for col, col_type in required_columns.items():
            if col not in existing_columns:
                c.execute(f'ALTER TABLE locations ADD COLUMN {col} {col_type}')
        conn.commit()


def get_tasks_for_month(user_id, year, month):
    conn = sqlite3.connect(DB_REMINDERS)
    c = conn.cursor()

    start_date = f'{year}-{month:02d}-01'
    if month == 12:
        end_date = f'{year + 1}-01-01'
    else:
        end_date = f'{year}-{month + 1:02d}-01'

    c.execute('''SELECT reminder_time, message 
                 FROM reminders 
                 WHERE user_id = ? AND reminder_time >= ? AND reminder_time < ? 
                 ORDER BY reminder_time''', (user_id, start_date, end_date))

    tasks = [(datetime.strptime(row[0], '%Y-%m-%d %H:%M:%S'), row[1])
             for row in c.fetchall()]
    conn.close()
    return tasks


def get_reminder_db_connection():
    return sqlite3.connect(DB_REMINDERS)


def get_location_db_connection():
    return sqlite3.connect(DB_LOCATIONS)
