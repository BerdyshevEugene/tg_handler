from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from service.service_messages import send_service_message


async def handle_service_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''
    здесь реализована рассылка служебных сообщений пользователю. Добавляйте в
    переменную "message"
    '''
    message = 'обновления: \n- тут должны быть обновления, но их нет'

    try:
        await send_service_message(message)
        logger.success(
            f'service messages have been sent to all users. Message {message}')
        await update.message.reply_text('служебные сообщения отправлены всем пользователям')
    except Exception as e:
        logger.error(f'failed to send service messages. Error: {str(e)}')
        await update.message.reply_text('не удалось отправить служебные сообщения')
