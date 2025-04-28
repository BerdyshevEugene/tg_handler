from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from loguru import logger
from handlers.month_handler import month_reminders
from service.location_storage import add_location
from service.reminder import (
    add_reminder, list_reminders, delete_reminder_by_index, parse_indices)
from service.db_connector import get_tasks_for_month
from service.states import ADD_REMINDER, DELETE_REMINDER


async def sendlocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        'пожалуйста, отправьте мневашу геопозицию, чтобы я мог отправлять вам задачи по расписанию')


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
    logger.debug(f'handle_add_reminder_finish called with update: {update}')
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
    '''запускает удаление напоминания. Нужно ввести номер'''
    logger.debug('handle_delete_reminder_start called')
    await update.callback_query.message.reply_text(
        'введите номер(а) напоминаний, которые хотите удалить'
    )
    return DELETE_REMINDER


async def handle_delete_reminder_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.debug(f'handle_delete_reminder_finish called with update: {update}')

    try:
        user_id = getattr(update.callback_query, 'from_user',
                          update.message.from_user).id
        text = update.effective_message.text.strip()
        logger.debug(f'user_id: {user_id}, text: {text}')

        indices = parse_indices(text)
        logger.debug(f'parsed indices: {indices}')

        if indices:
            successful, failed = delete_reminder_by_index(user_id, indices)
            logger.info(
                f'reminders deleted: success={successful}, failed={failed}')
            message = (f'удалены напоминания под номерами: {", ".join(str(idx + 1) for idx in successful)}'
                       if successful else 'напоминания с указанными номерами не найдены')
            await update.message.reply_text(message)
        else:
            await update.message.reply_text('введите номер(а) напоминания для удаления')

    except ValueError:
        logger.warning('invalid input format')
        await update.message.reply_text('неправильный формат. Введите номер(а) напоминания для удаления')
    except Exception as e:
        logger.error(f'произошла ошибка: {e}')
        await update.message.reply_text('произошла ошибка. Попробуйте еще раз или обратитесь к администратору')

    return ConversationHandler.END
