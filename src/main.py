import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler, ConversationHandler
)

from logger.logger import setup_logger
from location_storage import add_location
from weather import send_weather
from reminder import add_reminder, list_reminders, delete_reminder_by_index, daily_summary, parse_indices
from service.service_messages import send_service_message


load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
CHAT_ID = os.getenv('GROUP_ID')
bot = Bot(token=TG_BOT_TOKEN)
ADD_REMINDER, DELETE_REMINDER = range(2)


def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton('добавить напоминание',
                              callback_data='addreminder')],
        [InlineKeyboardButton('список напоминаний',
                              callback_data='listreminders')],
        [InlineKeyboardButton('удалить напоминание(-я)',
                              callback_data='deletereminder')],
        [InlineKeyboardButton('отправить местоположение',
                              callback_data='sendlocation')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        'Привет, выберите действие:',
        reply_markup=get_main_keyboard()
    )


async def handle_service_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = 'возможны ошибки'
    await send_service_message(message)
    await update.message.reply_text('служебные сообщения отправлены всем пользователям')


async def sendlocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text('пожалуйста, отправьте мне ваше местоположение, чтобы я мог отправлять вам прогноз погоды')


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_location = update.message.location
    chat_id = update.message.chat_id
    add_location(user_id, user_location.latitude,
                 user_location.longitude, chat_id)
    await update.message.reply_text('местоположение сохранено! Теперь я буду отправлять вам прогноз погоды по данной локации')


async def handle_add_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text('введите напоминание в одном из следующих форматов: \n- YYYY-MM-DD HH:MM ваше сообщение \n- 18 августа посмотреть фильм \n- послезавтра в 18:00 не забыть позвонить кому нибудь')
    return ADD_REMINDER


async def handle_add_reminder_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        user_id = update.callback_query.from_user.id
    else:
        user_id = update.message.from_user.id

    text = update.effective_message.text
    text_parts = text.split(' ', 2)

    if len(text_parts) < 3:
        await update.message.reply_text('неправильный формат. Введите повторно, используйте: YYYY-MM-DD HH:MM ваше сообщение')
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
        reminder_time = reminder_datetime.split()[1][:5]
        reminder_message = f'{reminder_datetime.split()[0]} {reminder_time}: {reminder[2]}'

        reminder_date = reminder_datetime.split()[0]

        if reminder_date != current_date:
            if i != 0:
                reminder_texts.append('')
            current_date = reminder_date

        reminder_texts.append(f'{i + 1}. {reminder_message}')
    response_text = '\n'.join(
        reminder_texts) if reminder_texts else 'напоминаний нет'
    await query.message.edit_text(response_text)


async def handle_delete_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text('введите номер напоминания для удаления')
    return DELETE_REMINDER


async def handle_delete_reminder_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        if update.callback_query:
            user_id = update.callback_query.from_user.id
            text = update.effective_message.text
        elif update.message:
            user_id = update.message.from_user.id
            text = update.message.text
        else:
            logger.error(
                'не удалось определить пользователя для удаления напоминания.')
            await update.message.reply_text('произошла ошибка. Попробуйте еще раз или обратитесь к администратору')
            return ConversationHandler.END

        indices = parse_indices(text.strip())

        if indices:
            successful_deletions, failed_deletions = delete_reminder_by_index(
                user_id, indices)

            if successful_deletions:
                await update.message.reply_text(f'удалено напоминание(-я) под номерами: {", ".join(str(idx + 1) for idx in successful_deletions)}')
            else:
                await update.message.reply_text('напоминания с указанными номерами не найдены')
        else:
            await update.message.reply_text('введите номер(а) напоминания для удаления')

    except ValueError:
        await update.message.reply_text('неправильный формат. Введите номер(а) напоминания для удаления')
        return ConversationHandler.END
    except Exception as e:
        logger.error(f'произошла ошибка: {e}')
        await update.message.reply_text('произошла ошибка. Попробуйте еще раз или обратитесь к администратору')

    return ConversationHandler.END


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

    return ConversationHandler.END

if __name__ == '__main__':
    setup_logger()
    application = Application.builder().token(TG_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button)],
        states={
            ADD_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_reminder_finish)],
            DELETE_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_reminder_finish)],
        },
        fallbacks=[],
    )

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('service', handle_service_message))
    application.add_handler(MessageHandler(filters.LOCATION, location))
    application.add_handler(conv_handler)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_weather, 'cron', hour=8, args=[bot, CHAT_ID])
    scheduler.add_job(send_weather, 'cron', hour=12, args=[bot, CHAT_ID])
    scheduler.add_job(send_weather, 'cron', hour=17,
                      minute=51, args=[bot, CHAT_ID])
    scheduler.add_job(send_weather, 'cron', hour=20,
                      minute=0, args=[bot, CHAT_ID])
    scheduler.add_job(daily_summary, 'cron', hour=17,
                      minute=52, args=[bot, CHAT_ID])
    scheduler.start()

    application.run_polling()
