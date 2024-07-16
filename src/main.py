import os
from dotenv import load_dotenv
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler
)

from logger.logger import setup_logger
from service.weather import send_weather
from service.reminder import daily_summary
from handlers import (
    start, handle_service_message, location, button,
    handle_add_reminder_finish, handle_delete_reminder_finish, ADD_REMINDER, DELETE_REMINDER
)

load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
CHAT_ID = os.getenv('GROUP_ID')
ADD_REMINDER, DELETE_REMINDER = range(2)

bot = Bot(token=TG_BOT_TOKEN)


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
