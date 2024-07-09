import datetime


from loguru import logger
from service.db_connector import get_reminder_db_connection, initialize_reminder_db

initialize_reminder_db()


def get_all_user_ids():
    conn = get_reminder_db_connection()
    c = conn.cursor()
    c.execute('SELECT DISTINCT user_id FROM reminders')
    user_ids = [row[0] for row in c.fetchall()]
    conn.close()
    logger.info(f'found user IDs: {user_ids}')
    return user_ids


def add_reminder(user_id, time_str, message):
    try:
        reminder_time = datetime.datetime.strptime(time_str, '%Y-%m-%d %H:%M')
    except ValueError as e:
        error_message = 'неправильный формат времени. Используйте формат: YYYY-MM-DD HH:MM'
        logger.error(
            f'failed to add reminder for user {user_id}: {error_message}. Error: {str(e)}')
        raise ValueError(error_message)

    conn = get_reminder_db_connection()
    c = conn.cursor()
    c.execute('INSERT INTO reminders (user_id, reminder_time, message) VALUES (?, ?, ?)',
              (user_id, reminder_time, message))
    conn.commit()
    conn.close()
    logger.info(
        f'Reminder added for user {user_id} at {reminder_time} with message: {message}')


def list_reminders(user_id):
    conn = get_reminder_db_connection()
    c = conn.cursor()
    c.execute(
        'SELECT * FROM reminders WHERE user_id=? ORDER BY reminder_time', (user_id,))
    reminders = c.fetchall()
    conn.close()
    logger.info(f'retrieved reminders for user {user_id}: {reminders}')
    return reminders


def delete_reminder_by_index(user_id, index):
    reminders = list_reminders(user_id)
    if index < 0 or index >= len(reminders):
        logger.warning(
            f'attempted to delete non-existent reminder at index {index} for user {user_id}')
        return False
    reminder_id = reminders[index][0]
    conn = get_reminder_db_connection()
    c = conn.cursor()
    c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
    conn.commit()
    conn.close()
    logger.info(
        f'deleted reminder {reminder_id} at index {index} for user {user_id}')
    return c.rowcount > 0


async def daily_summary(bot, chat_id):
    current_date = datetime.date.today()
    tomorrow_date = current_date + datetime.timedelta(days=1)
    user_ids = get_all_user_ids()

    for user_id in user_ids:
        reminders = list_reminders(user_id)

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
            message += 'на завтра задач нет'
        logger.info(f'sending daily summary to user {user_id}')
        await bot.send_message(chat_id=user_id, text=message)
    logger.info('daily summary job completed')
