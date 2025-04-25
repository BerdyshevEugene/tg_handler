from loguru import logger
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'user {update.effective_user.id} cancelled the conversation')
    await update.message.reply_text('диалог завершён')
    return ConversationHandler.END
