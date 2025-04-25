from loguru import logger

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'user {update.effective_user.id} cancelled the conversation')
    await update.message.reply_text('диалог завершён')
    return ConversationHandler.END
