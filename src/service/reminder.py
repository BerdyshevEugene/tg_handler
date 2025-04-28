import calendar
import datetime
import dateparser
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
        parsed_time = dateparser.parse(
            time_str, settings={'PREFER_DATES_FROM': 'future'})
        if not parsed_time:
            raise ValueError('не удалось распознать дату или время')
        if parsed_time.time() == datetime.time(0, 0):
            parsed_time = parsed_time.replace(hour=0, minute=0)
        reminder_time = parsed_time.replace(second=0, microsecond=0)
    except Exception as e:
        error_message = 'неправильный формат времени. Используйте что-то вроде: "завтра в 15:00" или "2023-12-31 15:00"'
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
        f'reminder added for user {user_id} at {reminder_time} with message: {message}')


def format_time(reminder_time):
    try:
        time_obj = datetime.datetime.strptime(
            reminder_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        time_obj = datetime.datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')

    if time_obj.time() == datetime.time(0, 0):
        return time_obj.strftime('%Y-%m-%d')
    else:
        return time_obj.strftime('%Y-%m-%d %H:%M')


def list_reminders(user_id):
    conn = get_reminder_db_connection()
    c = conn.cursor()
    c.execute(
        'SELECT * FROM reminders WHERE user_id=? ORDER BY reminder_time', (user_id,))
    reminders = c.fetchall()
    conn.close()

    formatted_reminders = [
        (reminder[0], format_time(reminder[1]), reminder[2])
        for reminder in reminders
    ]

    logger.info(
        f'retrieved reminders for user {user_id}: {formatted_reminders}')
    return formatted_reminders


def list_month_reminders(user_id, year, month):
    conn = get_reminder_db_connection()
    c = conn.cursor()

    start_date = f'{year}-{month:02d}-01'
    if month == 12:
        end_date = f'{year + 1}-01-01'
    else:
        end_date = f'{year}-{month + 1:02d}-01'

    c.execute(
        'SELECT reminder_time, message FROM reminders WHERE user_id = ? AND reminder_time >= ? AND reminder_time < ? ORDER BY reminder_time',
        (user_id, start_date, end_date)
    )
    reminders = c.fetchall()
    conn.close()

    reminders_by_day = {}
    for reminder_time, text in reminders:
        day = int(reminder_time.split('-')[2].split()[0])

        if day not in reminders_by_day:
            reminders_by_day[day] = ''
        reminders_by_day[day] += f'{text}\n                '

    return reminders_by_day


def delete_reminder_by_index(user_id, indices):
    reminders = list_reminders(user_id)
    successful_deletions = []
    failed_deletions = []
    conn = get_reminder_db_connection()
    c = conn.cursor()

    for index in indices:
        if index < 0 or index >= len(reminders):
            logger.warning(
                f'attempted to delete non-existent reminder at index {index} for user {user_id}')
            failed_deletions.append(index)
        else:
            reminder_id = reminders[index][0]
            c.execute('DELETE FROM reminders WHERE id = ?', (reminder_id,))
            successful_deletions.append(index)
    conn.commit()
    conn.close()

    if successful_deletions:
        logger.info(
            f'deleted reminders at indices {successful_deletions} for user {user_id}')
    if failed_deletions:
        logger.warning(
            f'failed to delete reminders at indices {failed_deletions} for user {user_id}')
    return successful_deletions, failed_deletions


def parse_indices(indices_str):
    indices = []
    for part in indices_str.split():
        if ',' in part:
            indices.extend(
                [int(x) - 1 for x in part.split(',') if x.isdigit()])
        elif part.isdigit():
            indices.append(int(part) - 1)
        else:
            logger.warning(f'wrong index format: {part}')
    return indices


def parse_reminder_time(reminder_time):
    try:
        return datetime.datetime.strptime(reminder_time, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        try:
            return datetime.datetime.strptime(reminder_time, '%Y-%m-%d %H:%M')
        except ValueError:
            return datetime.datetime.strptime(reminder_time, '%Y-%m-%d').replace(hour=0, minute=0)


async def daily_summary(bot, group_chat_id):
    current_date = datetime.date.today()
    tomorrow_date = current_date + datetime.timedelta(days=1)
    user_ids = get_all_user_ids()

    group_message = f'привет!\neжедневная сводка задач на сегодня, {current_date}:\n'
    tasks_today_group = []
    tasks_tomorrow_group = []

    for user_id in user_ids:
        reminders = list_reminders(user_id)

        tasks_today = [
            f'{i + 1}. {parse_reminder_time(reminder[1]).strftime("%H:%M")} {reminder[2]}'
            for i, reminder in enumerate(reminders)
            if parse_reminder_time(reminder[1]).date() == current_date
        ]
        tasks_tomorrow = [
            f'{i + 1}. {parse_reminder_time(reminder[1]).strftime("%H:%M")} {reminder[2]}'
            for i, reminder in enumerate(reminders)
            if parse_reminder_time(reminder[1]).date() == tomorrow_date
        ]

        user_message = f'привет!\nежедневная сводка задач на сегодня, {current_date}:\n'
        if tasks_today:
            user_message += '\n'.join(tasks_today)
        else:
            user_message += 'на сегодня задач нет\n'
        user_message += f'\n\nзапланировано на завтра, {tomorrow_date}:\n'
        if tasks_tomorrow:
            user_message += '\n'.join(tasks_tomorrow)
        else:
            user_message += 'на завтра задач нет'
        logger.info(f'sending daily summary to user {user_id}')
        await bot.send_message(chat_id=user_id, text=user_message)

        tasks_today_group.extend(tasks_today)
        tasks_tomorrow_group.extend(tasks_tomorrow)

    # формируем и отправляем групповое сообщение
    if tasks_today_group:
        group_message += '\n'.join(tasks_today_group)
    else:
        group_message += 'на сегодня задач нет\n'
    group_message += f'\n\nзапланировано на завтра, {tomorrow_date}:\n'
    if tasks_tomorrow_group:
        group_message += '\n'.join(tasks_tomorrow_group)
    else:
        group_message += 'на завтра задач нет'

    logger.info(f'sending daily summary to group {group_chat_id}')
    await bot.send_message(chat_id=group_chat_id, text=group_message)

    logger.info('daily summary job completed')
