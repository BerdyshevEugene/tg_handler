import os
import pytz

from dotenv import load_dotenv
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram import Bot
from telegram.ext import (
    Application, CommandHandler, MessageHandler, filters,
    CallbackQueryHandler, ConversationHandler
)

from logger.logger import setup_logger
# from service.weather import send_weather
from service.reminder import daily_summary
from handler import (
    start, handle_service_message, location, button,
    handle_add_reminder_finish, handle_delete_reminder_finish, ADD_REMINDER, DELETE_REMINDER
)
from location_storage import get_all_locations


load_dotenv()
TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
CHAT_ID = os.getenv('GROUP_ID')
ADD_REMINDER, DELETE_REMINDER = range(2)

bot = Bot(token=TG_BOT_TOKEN)


# async def schedule_user_weather_jobs(context):
#     locations = get_all_locations()
#     for user_id, latitude, longitude, chat_id, timezone_str in locations:
#         user_timezone = pytz.timezone(timezone_str)
#         current_time = datetime.now(user_timezone)

#         # Пример расписания: 8:00, 12:00, 17:00 и 20:00 по местному времени пользователя
#         schedule_times = [
#             current_time.replace(hour=8, minute=0, second=0, microsecond=0),
#             current_time.replace(hour=12, minute=0, second=0, microsecond=0),
#             current_time.replace(hour=17, minute=40, second=0, microsecond=0),
#             current_time.replace(hour=20, minute=0, second=0, microsecond=0)
#         ]

#         for schedule_time in schedule_times:
#             if schedule_time < current_time:
#                 schedule_time += timedelta(days=1)
#             scheduler.add_job(send_weather, 'date', run_date=schedule_time, args=[
#                               bot, user_id, chat_id, latitude, longitude])


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

    scheduler.add_job(daily_summary, 'cron', hour=8,
                      minute=55, args=[bot, CHAT_ID])
    # application.job_queue.run_once(schedule_user_weather_jobs, 0)

    scheduler.start()
    application.run_polling()
