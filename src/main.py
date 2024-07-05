import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    ContextTypes, CallbackQueryHandler, ConversationHandler
)

from weather import send_weather
from reminder import add_reminder, list_reminders, delete_reminder_by_index, daily_summary
from location_storage import add_location

load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
chat_id = os.getenv('GROUP_ID')
bot = Bot(token=TG_BOT_TOKEN)

ADD_REMINDER, DELETE_REMINDER = range(2)


def get_main_keyboard():
    keyboard = [
        [InlineKeyboardButton('добавить напоминание',
                              callback_data='addreminder')],
        [InlineKeyboardButton('список напоминаний',
                              callback_data='listreminders')],
        [InlineKeyboardButton('удалить напоминание',
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


async def sendlocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text('пожалуйста, отправьте мне ваше местоположение, чтобы я мог отправлять вам прогноз погоды.')


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_location = update.message.location
    add_location(user_id, user_location.latitude, user_location.longitude)
    await update.message.reply_text('местоположение сохранено! Теперь я буду отправлять вам прогноз погоды')


async def handle_add_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text('Введите напоминание в формате: YYYY-MM-DD HH:MM ваше сообщение')
    return ADD_REMINDER


async def handle_add_reminder_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    text_parts = text.split(' ', 2)
    if len(text_parts) < 3:
        await update.message.reply_text('неправильный формат. Используйте: YYYY-MM-DD HH:MM ваше сообщение')
        return ADD_REMINDER

    time_str = f'{text_parts[0]} {text_parts[1]}'
    message = text_parts[2]
    add_reminder(time_str, message)
    await update.message.reply_text('напоминание добавлено')
    return ConversationHandler.END


async def handle_list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminders = list_reminders()
    reminder_texts = [
        f'{i + 1}. {reminder[1]}: {reminder[2]}' for i, reminder in enumerate(reminders)]
    response_text = '\n'.join(
        reminder_texts) if reminder_texts else 'напоминаний нет'

    if update.message:
        await update.message.reply_text(response_text)
    elif update.callback_query:
        await update.callback_query.message.edit_text(response_text)


async def handle_delete_reminder_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.message.reply_text('введите номер напоминания для удаления')
    return DELETE_REMINDER


async def handle_delete_reminder_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    try:
        reminder_index = int(text) - 1
        if delete_reminder_by_index(reminder_index):
            await update.message.reply_text('напоминание удалено')
        else:
            await update.message.reply_text('напоминания с таким номером не найдено')
    except ValueError:
        await update.message.reply_text('неправильный формат. Введите номер напоминания')
        return DELETE_REMINDER

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
    application.add_handler(MessageHandler(filters.LOCATION, location))
    application.add_handler(conv_handler)

    scheduler = AsyncIOScheduler()
    scheduler.add_job(send_weather, 'cron', hour=8, args=[bot, chat_id])
    scheduler.add_job(send_weather, 'cron', hour=12, args=[bot, chat_id])
    scheduler.add_job(send_weather, 'cron', hour=17,
                      minute=40, args=[bot, chat_id])
    scheduler.add_job(send_weather, 'cron', hour=21, args=[bot, chat_id])
    scheduler.add_job(daily_summary, 'cron', hour=10,
                      minute=00, args=[bot, chat_id])
    scheduler.start()

    application.run_polling()
