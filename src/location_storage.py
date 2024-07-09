from timezonefinder import TimezoneFinder
from service.db_connector import get_location_db_connection, initialize_location_db

tf = TimezoneFinder()
initialize_location_db()


def add_location(user_id, latitude, longitude, chat_id):
    timezone = tf.timezone_at(lat=latitude, lng=longitude)
    conn = get_location_db_connection()
    c = conn.cursor()
    c.execute('REPLACE INTO locations (user_id, latitude, longitude, chat_id, timezone) VALUES (?, ?, ?, ?, ?)',
              (user_id, latitude, longitude, chat_id, timezone))
    conn.commit()
    conn.close()


def get_location(user_id):
    conn = get_location_db_connection()
    c = conn.cursor()
    c.execute(
        'SELECT latitude, longitude, chat_id, timezone FROM locations WHERE user_id = ?', (user_id,))
    location = c.fetchone()
    conn.close()
    return location


def get_all_locations():
    conn = get_location_db_connection()
    c = conn.cursor()
    c.execute(
        'SELECT user_id, latitude, longitude, chat_id, timezone FROM locations')
    locations = c.fetchall()
    conn.close()
    return locations
