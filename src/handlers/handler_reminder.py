from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import ContextTypes, ConversationHandler

from handlers.handler_logic import handle_add_reminder_start
from service.states import (
    ADD_REMINDER, CHOOSE_REMINDER_TYPE, CHOOSE_REMINDER_FREQUENCY
    )
from mrkup.keyboard_constants import KEYBOARD


async def handle_choose_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE):
    freq = update.message.text.lower()
    valid_freqs = {'ежедневно', 'еженедельно', 'ежемесячно', 'ежегодно'}

    if freq.lower() in {value.lower() for value in KEYBOARD.values() if value in valid_freqs}:
        context.user_data['reminder_frequency'] = freq
        await update.message.reply_text(
            f'введите напоминание (частота: {freq}):',
            reply_markup=context.bot_data['keyboards'].remove_menu()
        )
        return ADD_REMINDER

    elif freq == KEYBOARD['<<'].lower():
        return await handle_add_reminder_start(update, context)

    await update.message.reply_text('неизвестная частота, выберите один из вариантов на клавиатуре')
    return CHOOSE_REMINDER_FREQUENCY


async def handle_choose_reminder_type(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()

    if text == KEYBOARD['одноразовое'].lower():
        await update.message.reply_text(
            'введите напоминание в формате: \n- YYYY-MM-DD HH:MM ваше сообщение\n\nили в свободной форме (например: "завтра в 18:00 созвон")',
            reply_markup=context.bot_data['keyboards'].remove_menu()
        )
        return ADD_REMINDER

    elif text == KEYBOARD['регулярное'].lower():
        await update.message.reply_text(
            'выберите периодичность:',
            reply_markup=context.bot_data['keyboards'].frequency_menu()
        )
        return CHOOSE_REMINDER_FREQUENCY

    elif text == KEYBOARD['<<'].lower():
        await update.message.reply_text(
            'главное меню:',
            reply_markup=context.bot_data['keyboards'].start_menu()
        )
        return ConversationHandler.END

    await update.message.reply_text('неизвестный тип, выберите один из вариантов на клавиатуре')
    return CHOOSE_REMINDER_TYPE