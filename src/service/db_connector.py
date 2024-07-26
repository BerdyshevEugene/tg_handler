import sqlite3

DB_REMINDERS = 'reminders.db'
DB_LOCATIONS = 'locations.db'


def initialize_reminder_db():
    conn = sqlite3.connect(DB_REMINDERS)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS reminders
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                 user_id INTEGER,
                 reminder_time TIMESTAMP,
                 message TEXT)''')
    conn.commit()
    c.execute('PRAGMA table_info(reminders)')
    columns = [column[1] for column in c.fetchall()]
    if 'user_id' not in columns:
        c.execute('ALTER TABLE reminders ADD COLUMN user_id INTEGER')
    if 'reminder_time' not in columns:
        c.execute('ALTER TABLE reminders ADD COLUMN reminder_time TIMESTAMP')
    if 'message' not in columns:
        c.execute('ALTER TABLE reminders ADD COLUMN message TEXT')
    conn.commit()
    conn.close()


def initialize_location_db():
    conn = sqlite3.connect(DB_LOCATIONS)
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
    c.execute('PRAGMA table_info(locations)')
    columns = [column[1] for column in c.fetchall()]
    if 'latitude' not in columns:
        c.execute('ALTER TABLE locations ADD COLUMN latitude REAL')
    if 'longitude' not in columns:
        c.execute('ALTER TABLE locations ADD COLUMN longitude REAL')
    if 'chat_id' not in columns:
        c.execute('ALTER TABLE locations ADD COLUMN chat_id INTEGER')
    if 'timezone' not in columns:
        c.execute('ALTER TABLE locations ADD COLUMN timezone TEXT')
    if 'hour' not in columns:
        c.execute('ALTER TABLE locations ADD COLUMN hour INTEGER')
    if 'minute' not in columns:
        c.execute('ALTER TABLE locations ADD COLUMN minute INTEGER')
    conn.commit()
    conn.close()


def get_reminder_db_connection():
    return sqlite3.connect(DB_REMINDERS)


def get_location_db_connection():
    return sqlite3.connect(DB_LOCATIONS)
