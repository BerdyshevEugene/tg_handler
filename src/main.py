import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from weather import send_weather
from reminder import add_reminder, list_reminders, delete_reminder_by_index, daily_summary
from location_storage import add_location

load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
chat_id = os.getenv('GROUP_ID')
bot = Bot(token=TG_BOT_TOKEN)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands_list = [
        '/start - Начать взаимодействие с ботом',
        '/addreminder YYYY-MM-DD HH:MM ваше_сообщение - Добавить напоминание',
        '/listreminders - Показать список текущих напоминаний',
        '/deletereminder номер - Удалить напоминание по номеру',
        '/sendlocation - Отправьте ваше местоположение, чтобы получать прогноз погоды'
    ]
    await update.message.reply_text('Привет! Список команд:\n' + '\n'.join(commands_list))


async def sendlocation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Пожалуйста, отправьте мне ваше местоположение, чтобы я мог отправлять вам прогноз погоды.')


async def location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_location = update.message.location
    add_location(user_id, user_location.latitude, user_location.longitude)
    await update.message.reply_text('Местоположение сохранено! Теперь я буду отправлять вам прогноз погоды.')


async def handle_add_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        time_str = context.args[0] + ' ' + context.args[1]
        message = ' '.join(context.args[2:])
        add_reminder(time_str, message)
        await update.message.reply_text('напоминание добавлено')
    except (IndexError, ValueError):
        await update.message.reply_text('неправильный формат. Используйте: /addreminder YYYY-MM-DD HH:MM <ваше_сообщение>')


async def handle_list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reminders = list_reminders()
    reminder_texts = [
        f'{i + 1}. {reminder[1]}: {reminder[2]}' for i, reminder in enumerate(reminders)]
    if reminder_texts:
        await update.message.reply_text('\n'.join(reminder_texts))
    else:
        await update.message.reply_text('напоминаний нет')


async def handle_delete_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        reminder_index = int(context.args[0]) - 1
        if delete_reminder_by_index(reminder_index):
            await update.message.reply_text('напоминание удалено')
        else:
            await update.message.reply_text('напоминание с таким номером не найдено')
    except (IndexError, ValueError):
        await update.message.reply_text('неправильный формат. Используйте: /deletereminder <номер>')


if __name__ == '__main__':
    application = Application.builder().token(TG_BOT_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('sendlocation', sendlocation))
    application.add_handler(MessageHandler(filters.LOCATION, location))
    application.add_handler(CommandHandler('addreminder', handle_add_reminder))
    application.add_handler(CommandHandler(
        'listreminders', handle_list_reminders))
    application.add_handler(CommandHandler(
        'deletereminder', handle_delete_reminder))

    scheduler = AsyncIOScheduler()
    # scheduler.add_job(send_weather, 'interval', hours=3, args=[bot, chat_id])
    scheduler.add_job(send_weather, 'cron', hour=8, args=[bot, chat_id])
    scheduler.add_job(send_weather, 'cron', hour=12, args=[bot, chat_id])
    scheduler.add_job(send_weather, 'cron', hour=17,
                      minute=40, args=[bot, chat_id])
    scheduler.add_job(send_weather, 'cron', hour=21, args=[bot, chat_id])
    scheduler.add_job(daily_summary, 'cron', hour=20,
                      minute=18, args=[bot, chat_id])
    scheduler.start()

    application.run_polling()
