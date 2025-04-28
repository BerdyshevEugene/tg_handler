from loguru import logger
from datetime import datetime
from telegram import Bot, Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes, ConversationHandler

from handlers.month_handler import month_reminders
from handlers.handler import (
    handle_add_reminder_start, handle_list_reminders,
    handle_delete_reminder_start, sendlocation)


def get_main_keyboard(now: datetime):
    '''
    создает и возвращает главное меню в виде клавиатуры с кнопками для
    взаимодействия с пользователем
    '''
    current_year = now.year
    current_month = now.month
    keyboard = [
        [InlineKeyboardButton('добавить напоминание',
                              callback_data='addreminder')],
        [InlineKeyboardButton('список напоминаний',
                              callback_data='listreminders')],
        [InlineKeyboardButton('удалить напоминание(-я)',
                              callback_data='deletereminder')],
        [InlineKeyboardButton('отправить местоположение',
                              callback_data='sendlocation')],
        [InlineKeyboardButton(
            'показать календарь (тестовый функционал)', callback_data=f'showcalendar_{current_month}_{current_year}')]
    ]
    return InlineKeyboardMarkup(keyboard)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''запускает основное меню бота с листом команд'''
    now = datetime.now()
    await update.message.reply_text(
        'выберите действие:',
        reply_markup=get_main_keyboard(now)
    )


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f'user {update.effective_user.id} cancelled the conversation')
    await update.message.reply_text('диалог завершён')
    return ConversationHandler.END


async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    command = query.data
    logger.debug(f'button pressed: {command}')

    if command == 'addreminder':
        return await handle_add_reminder_start(update, context)
    elif command == 'listreminders':
        await handle_list_reminders(update, context)
    elif command == 'deletereminder':
        return await handle_delete_reminder_start(update, context)
    elif command == 'sendlocation':
        await sendlocation(update, context)
    elif command.startswith('showcalendar_'):
        await month_reminders(update, context)

    return ConversationHandler.END
