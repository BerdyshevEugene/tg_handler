import sqlite3

DATABASE = 'locations.db'


def initialize_database():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS locations
                 (user_id INTEGER PRIMARY KEY,
                 latitude REAL,
                 longitude REAL,
                 chat_id INTEGER)''')
    conn.commit()
    conn.close()


initialize_database()


def add_location(user_id, latitude, longitude, chat_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('REPLACE INTO locations (user_id, latitude, longitude, chat_id) VALUES (?, ?, ?, ?)',
              (user_id, latitude, longitude, chat_id))
    conn.commit()
    conn.close()


def get_location(user_id):
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute(
        'SELECT latitude, longitude, chat_id FROM locations WHERE user_id = ?', (user_id,))
    location = c.fetchone()
    conn.close()
    return location


def get_all_locations():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('SELECT user_id, latitude, longitude, chat_id FROM locations')
    locations = c.fetchall()
    conn.close()
    return locations
