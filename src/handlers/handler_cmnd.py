from telegram.ext import (
    CommandHandler, MessageHandler, filters, 
    CallbackQueryHandler, ConversationHandler
)
from telegram import Update
from telegram.ext import ContextTypes
from loguru import logger
from handlers.handler_logic import (
    handle_add_reminder_start, handle_list_reminders,
    handle_delete_reminder_start, handle_add_reminder_finish,
    handle_delete_reminder_finish, location
)
from handlers.handler_reminder import (
    handle_choose_reminder_type, handle_choose_frequency)
from handlers.handler import Handler
from handlers.month_handler import month_reminders
from handlers.service_message_handler import handle_service_message
from mrkup.keyboard_constants import KEYBOARD
from service.states import (
    ADD_REMINDER, DELETE_REMINDER,
    CHOOSE_REMINDER_TYPE, CHOOSE_REMINDER_FREQUENCY
)


class HandlerCommands(Handler):
    '''обработка команд и callback'ов с использованием reply-клавиатуры'''
    def __init__(self, bot):
        super().__init__(bot)
        self.application = bot.application
        self.application.bot_data['keyboards'] = self.keyboards

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''обработка команды /start с reply-клавиатурой'''
        await update.message.reply_text(
            'выберите действие:',
            reply_markup=self.keyboards.start_menu()
        )

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''обработка отмены'''
        logger.info(f'пользователь {update.effective_user.id} отменил действие')
        await update.message.reply_text(
            'действие отменено',
            reply_markup=self.keyboards.start_menu()
        )
        return ConversationHandler.END

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        '''обработка текстовых сообщений с кнопок'''
        text = update.message.text
        if text == KEYBOARD['список напоминаний']:
            await handle_list_reminders(update, context)
        elif text == KEYBOARD['добавить напоминание']:
            return await handle_add_reminder_start(update, context)
        elif text == KEYBOARD['удалить напоминание']:
            return await handle_delete_reminder_start(update, context)
        elif text == KEYBOARD['показать календарь']:
            await month_reminders(update, context)
        elif text == KEYBOARD['инфо']:
            await update.message.reply_text(
                'Привет! Я бот для ведения заметок и напоминаний \n\nв данный момент я могу: \n- работать с напоминаниями \n- отображать задачи на текущий месяц',
                reply_markup=self.keyboards.info_menu()
            )
        elif text == KEYBOARD['<<']:
            await update.message.reply_text(
                'главное меню:',
                reply_markup=self.keyboards.start_menu()
            )

    def handle(self):
        '''регистрация обработчиков'''
        self.application.add_handler(CommandHandler('start', self.start))
        self.application.add_handler(CommandHandler('service', handle_service_message))
        self.application.add_handler(CommandHandler('month', month_reminders))
        self.application.add_handler(MessageHandler(filters.LOCATION, location))

        conv_handler = ConversationHandler(
            entry_points=[
                MessageHandler(filters.Regex(KEYBOARD['добавить напоминание']), handle_add_reminder_start),
                MessageHandler(filters.Regex(KEYBOARD['удалить напоминание']), handle_delete_reminder_start)
            ],
        states={
            CHOOSE_REMINDER_TYPE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choose_reminder_type)],
            CHOOSE_REMINDER_FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_choose_frequency)],
            ADD_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_add_reminder_finish)],
            DELETE_REMINDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_delete_reminder_finish)],
        },
        fallbacks=[CommandHandler('cancel', self.cancel)],
        )
        self.application.add_handler(conv_handler)

        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
