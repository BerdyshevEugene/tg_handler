import os
import sys
import signal

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from datetime import datetime, timedelta
from telegram import Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler
)
from telegram.warnings import PTBUserWarning

from handlers.month_handler import month_reminders
from handlers.handler import (
    start, location, button,
    handle_add_reminder_finish, handle_delete_reminder_finish)
from handlers.service_message_handler import handle_service_message
from handlers.base_handler import cancel
from logger.logger import setup_logger
from service.reminder import daily_summary
from service.states import ADD_REMINDER, DELETE_REMINDER


load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
CHAT_ID = os.getenv('GROUP_ID')

bot = Bot(token=TG_BOT_TOKEN)


def stop_handler(signal, frame):
    logger.info('bot stopped')
    scheduler.shutdown()
    application.stop()
    sys.exit(0)


if __name__ == '__main__':
    try:
        logger = setup_logger()
        application = Application.builder().token(TG_BOT_TOKEN).build()
        logger.info('START registering command handlers')

        conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(button)],
            states={
                ADD_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_reminder_finish)],
                DELETE_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_reminder_finish)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True,
        )

        application.add_handler(CommandHandler('start', start))
        application.add_handler(CommandHandler(
            'service', handle_service_message))
        application.add_handler(CommandHandler('month', month_reminders))
        application.add_handler(MessageHandler(filters.LOCATION, location))
        application.add_handler(conv_handler)

        # планировщик задач
        scheduler = AsyncIOScheduler()
        scheduler.add_job(daily_summary, 'cron', hour=8,
                          minute=30, args=[bot, CHAT_ID])
        logger.info('the scheduler is set to run daily at 8:30 a.m.')
        scheduler.start()
        signal.signal(signal.SIGINT, stop_handler)
        signal.signal(signal.SIGTERM, stop_handler)
        application.run_polling()
    except Exception as e:
        logger.critical(f'bot crashed with error: {e}')
