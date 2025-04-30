# main.py
import os
import sys
import signal
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from dotenv import load_dotenv
from telegram import Bot
from telegram.ext import Application
from logger.logger import setup_logger
from service.reminder import daily_summary
from handlers.handler_main import HandlerMain


load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')


class TelegramBot:
    '''основной класс телеграм бота'''
    def __init__(self):
        '''инициализация бота'''
        self.token = TG_BOT_TOKEN
        self.bot = Bot(token=self.token)
        self.scheduler = AsyncIOScheduler()
        self.application = Application.builder().token(self.token).build()
        self.logger = setup_logger()
        self.handler_main = HandlerMain(self)

    def stop_handler(self, signal, frame):
        '''обработчик остановки бота'''
        self.logger.info('bot stopped')
        self.scheduler.shutdown()
        self.application.stop()
        sys.exit(0)

    def schedule_jobs(self):
        '''настройка планировщика задач'''
        self.scheduler.add_job(daily_summary, 'cron',
                             hour=8, minute=30, args=[self.bot, GROUP_ID])
        self.logger.info('the scheduler is set to run daily at 8:30 a.m.')

    def run(self):
        '''запуск бота'''
        self.handler_main.handle()
        self.schedule_jobs()

        self.scheduler.start()

        signal.signal(signal.SIGINT, self.stop_handler)
        signal.signal(signal.SIGTERM, self.stop_handler)

        self.application.run_polling()


if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()