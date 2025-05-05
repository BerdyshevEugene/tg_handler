import calendar

from datetime import datetime
from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from loguru import logger
from service.location_storage import add_location
from service.reminder import (
    add_reminder, list_reminders, delete_reminder_by_index, parse_indices)
from service.states import ADD_REMINDER, DELETE_REMINDER, CHOOSE_REMINDER_TYPE


async def sendlocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text(
        'пожалуйста, отправьте мне вашу геопозицию, чтобы я мог отправлять вам задачи по расписанию')


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_location = update.message.location
    chat_id = update.message.chat_id
    add_location(user_id, user_location.latitude,
                 user_location.longitude, chat_id)
    await update.message.reply_text('сохранено!')


async def handle_add_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'выберите тип напоминания:',
        reply_markup=context.bot_data['keyboards'].reminder_type_menu()
    )
    return CHOOSE_REMINDER_TYPE


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
        await update.message.reply_text(
            'напоминание добавлено',
            reply_markup=context.bot_data['keyboards'].start_menu()
        )
        return ConversationHandler.END
    except ValueError as e:
        await update.message.reply_text(str(e))
        return ADD_REMINDER


async def handle_list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        user_id = query.from_user.id
    else:
        user_id = update.message.from_user.id  # Для случая, если это обычное сообщение, а не callback

    reminders = list_reminders(user_id)

    reminder_texts = []
    current_month = None

    month_names_ru = {
        1: 'Январь', 2: 'Февраль', 3: 'Март', 4: 'Апрель',
        5: 'Май', 6: 'Июнь', 7: 'Июль', 8: 'Август',
        9: 'Сентябрь', 10: 'Октябрь', 11: 'Ноябрь', 12: 'Декабрь'
    }

    for i, reminder in enumerate(reminders):
        reminder_datetime = reminder[1]
        reminder_parts = reminder_datetime.split()

        reminder_date = reminder_parts[0]
        formatted_date = f'{reminder_date.split("-")[2]}/{reminder_date.split("-")[1]}'

        month_year = reminder_date[:7]
        year, month = reminder_date.split('-')[:2]
        month = int(month)

        month_name = month_names_ru[month]

        if month_year != current_month:
            if current_month:
                reminder_texts.append('')
            reminder_texts.append(f'<b>{month_name} {year}:</b>')
            current_month = month_year

        reminder_message = f'<b>{formatted_date}:</b> {reminder[2]}'
        reminder_texts.append(f'{i + 1}. {reminder_message}')

    response_text = '\n'.join(
        reminder_texts) if reminder_texts else 'напоминаний нет'
    if query:
        await query.message.edit_text(response_text, parse_mode=ParseMode.HTML)
    else:
        await update.message.reply_text(response_text, parse_mode=ParseMode.HTML)


async def handle_delete_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''запускает удаление напоминания. Нужно ввести номер'''
    if update.callback_query:
        await update.callback_query.message.reply_text(
            'введите номер(а) напоминаний, которые хотите удалить'
        )
    else:
        await update.message.reply_text(
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
            await update.message.reply_text('введите номер(-а) напоминания для удаления')

    except ValueError:
        logger.warning('invalid input format')
        await update.message.reply_text('неправильный формат. Введите номер(-а) напоминания для удаления')
    except Exception as e:
        logger.error(f'error when deleting: {e}')
        await update.message.reply_text('произошла ошибка. Попробуйте еще раз или обратитесь к администратору')

    return ConversationHandler.END