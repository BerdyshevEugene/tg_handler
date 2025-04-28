import os
import sys
import signal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler
)
from handlers.month_handler import month_reminders
from handlers.base_handler import cancel, start, button
from handlers.handler import (
    location, handle_add_reminder_finish, handle_delete_reminder_finish)
from handlers.service_message_handler import handle_service_message
from logger.logger import setup_logger
from service.reminder import daily_summary
from service.states import ADD_REMINDER, DELETE_REMINDER


load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
CHAT_ID = os.getenv('GROUP_ID')


class TelegramBot:
    '''
    основной класс телеграм бота
    '''

    def __init__(self):
        '''инициализация бота'''
        self.token = TG_BOT_TOKEN
        self.bot = Bot(token=self.token)
        self.scheduler = AsyncIOScheduler()
        self.application = Application.builder().token(self.token).build()
        self.logger = setup_logger()

    def stop_handler(self, signal, frame):
        '''обработчик остановки бота при получении сигнала'''
        self.logger.info('bot stopped')
        self.scheduler.shutdown()
        self.application.stop()
        sys.exit(0)

    def add_handlers(self):
        '''
        добавление всех обработчиков команд и событий
        '''
        self.application.add_handler(CommandHandler('start', start))
        self.application.add_handler(
            CommandHandler('service', handle_service_message))
        self.application.add_handler(CommandHandler('month', month_reminders))
        self.application.add_handler(
            MessageHandler(filters.LOCATION, location))

        # обработчики для добавления и удаления напоминаний
        conv_handler = ConversationHandler(
            entry_points=[CallbackQueryHandler(button)],
            states={
                ADD_REMINDER: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_add_reminder_finish)],
                DELETE_REMINDER: [MessageHandler(
                    filters.TEXT & ~filters.COMMAND, handle_delete_reminder_finish)],
            },
            fallbacks=[CommandHandler('cancel', cancel)],
            per_chat=True,
        )
        self.application.add_handler(conv_handler)

    def schedule_jobs(self):
        '''настройка планировщика задач (например, ежедневные отчеты)'''
        self.scheduler.add_job(daily_summary, 'cron',
                               hour=8, minute=30, args=[self.bot, CHAT_ID])
        self.logger.info('the scheduler is set to run daily at 8:30 a.m.')

    def run(self):
        self.add_handlers()
        self.schedule_jobs()

        self.scheduler.start()

        signal.signal(signal.SIGINT, self.stop_handler)
        signal.signal(signal.SIGTERM, self.stop_handler)

        self.application.run_polling()


if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()
