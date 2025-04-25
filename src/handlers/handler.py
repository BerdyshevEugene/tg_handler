from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime

from location_storage import add_location
from service.reminder import (
    add_reminder, list_reminders, delete_reminder_by_index, parse_indices)
from service.service_messages import send_service_message
from service.db_connector import get_tasks_for_month
from calendar_handler.calendar_generator import generate_calendar_image
import logging

logger = logging.getLogger(__name__)

ADD_REMINDER, DELETE_REMINDER = range(2)


def get_main_keyboard():
    '''
    создает и возвращает главное меню в виде клавиатуры с кнопками для
    взаимодействия с пользователем
    '''
    current_year = datetime.now().year
    current_month = datetime.now().month
    keyboard = [
        [InlineKeyboardButton('добавить напоминание',
                              callback_data='addreminder')],
        [InlineKeyboardButton('список напоминаний',
                              callback_data='listreminders')],
        [InlineKeyboardButton('удалить напоминание(-я)',
                              callback_data='deletereminder')],
        [InlineKeyboardButton('отправить местоположение',
                              callback_data='sendlocation')],
        [InlineKeyboardButton(
            'показать календарь (тестовый функционал)', callback_data=f'showcalendar_{current_month}_{current_year}')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'выберите действие:',
        reply_markup=get_main_keyboard()
    )


async def handle_service_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    здесь реализована рассылка служебных сообщений пользователю. Добавляять в
    переменную "message"
    '''
    message = 'обновления: \n- тут должны быть обновления, но их нет'
    await send_service_message(message)
    await update.message.reply_text('служебные сообщения отправлены всем пользователям')


async def sendlocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text('пожалуйста, отправьте мне вашу геопозицию, чтобы я мог отправлять вам задачи по расписанию')


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_location = update.message.location
    chat_id = update.message.chat_id
    add_location(user_id, user_location.latitude,
                 user_location.longitude, chat_id)
    await update.message.reply_text('сохранено!')


async def handle_add_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        'введите напоминание в одном из следующих форматов: \n- YYYY-MM-DD HH:MM ваше сообщение \n- 18 августа посмотреть фильм \n- послезавтра в 18:00 не забыть позвонить кому нибудь \n\n чтобы отменить ввод, введите "отмена" или "cancel"'
    )
    return ADD_REMINDER


async def handle_add_reminder_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.message.from_user.id

    text = update.effective_message.text
    if text.lower() == 'отмена' or text.lower() == 'cancel':
        await update.message.reply_text('ввод напоминания отменен. Вы можете выбрать другое действие')
        return ConversationHandler.END
    text_parts = text.split(' ', 2)

    if len(text_parts) < 3:
        await update.message.reply_text(
            'неправильный формат. Введите повторно, используйте: YYYY-MM-DD HH:MM ваше сообщение'
        )
        return ADD_REMINDER

    time_str = f'{text_parts[0]} {text_parts[1]}'
    message = text_parts[2]

    try:
        add_reminder(user_id, time_str, message)
        await update.message.reply_text('напоминание добавлено')
        return ConversationHandler.END
    except ValueError as e:
        await update.message.reply_text(str(e))
        return ADD_REMINDER


async def handle_list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    reminders = list_reminders(user_id)

    reminder_texts = []
    current_date = None

    for i, reminder in enumerate(reminders):
        reminder_datetime = reminder[1]
        reminder_parts = reminder_datetime.split()

        if len(reminder_parts) > 1:
            reminder_time = reminder_parts[1][:5]
        else:
            reminder_time = ""

        reminder_message = f'{reminder_parts[0]} {reminder_time}: {reminder[2]}' if reminder_time else f'{reminder_parts[0]}: {reminder[2]}'

        reminder_date = reminder_parts[0]
        if reminder_date != current_date:
            if i != 0:
                reminder_texts.append('')
            current_date = reminder_date

        reminder_texts.append(f'{i + 1}. {reminder_message}')

    response_text = '\n'.join(
        reminder_texts) if reminder_texts else 'напоминаний нет'
    await query.message.edit_text(response_text)


async def handle_delete_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    запускает удаление напоминания. Нужно ввести номер
    '''
    await update.callback_query.message.reply_text('введите номер напоминания для удаления')
    return DELETE_REMINDER


async def handle_delete_reminder_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = getattr(update.callback_query, 'from_user',
                          update.message.from_user).id
        text = update.effective_message.text.strip()
        indices = parse_indices(text)

        if indices:
            successful, failed = delete_reminder_by_index(user_id, indices)
            message = (f'удалены напоминания под номерами: {", ".join(str(idx + 1) for idx in successful)}'
                       if successful else 'напоминания с указанными номерами не найдены')
            await update.message.reply_text(message)
        else:
            await update.message.reply_text('введите номер(а) напоминания для удаления')

    except ValueError:
        await update.message.reply_text('неправильный формат. Введите номер(а) напоминания для удаления')
    except Exception as e:
        logger.error(f'произошла ошибка: {e}')
        await update.message.reply_text('произошла ошибка. Попробуйте еще раз или обратитесь к администратору')

    return ConversationHandler.END


async def handle_show_calendar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Разбор данных из callback_data
    data = query.data.split('_')
    if len(data) != 3:
        await query.message.reply_text('неверный формат данных для календаря.')
        return

    command, month, year = data[0], int(data[1]), int(data[2])
    if command != 'showcalendar':
        return

    user_id = query.from_user.id
    tasks = get_tasks_for_month(user_id, year, month)

    try:
        calendar_image_path = generate_calendar_image(year, month, tasks)

        with open(calendar_image_path, 'rb') as photo:
            await query.message.reply_photo(photo)

    except Exception as e:
        logger.error(f'error generating the calendar: {e}')
        await query.message.reply_text('не удалось сгенерировать календарь')


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    command = query.data

    if command == 'addreminder':
        return await handle_add_reminder_start(update, context)
    elif command == 'listreminders':
        await handle_list_reminders(update, context)
    elif command == 'deletereminder':
        return await handle_delete_reminder_start(update, context)
    elif command == 'sendlocation':
        await sendlocation(update, context)
    elif command.startswith('showcalendar_'):
        await handle_show_calendar(update, context)

    return ConversationHandler.END
