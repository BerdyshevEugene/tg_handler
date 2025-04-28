import os
from emoji import emojize

VERSION = '1.0.1'
AUTHOR = 'E.N.'
TOKEN = os.getenv('TG_BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')


# # родительская директория
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# # путь до базы данных
# DATABASE = os.path.join('sqlite:///'+BASE_DIR, NAME_DB)

# COUNT = 0

# # кнопки управления
# KEYBOARD = {
#     'CHOOSE_GOODS': emojize(':open_file_folder: Выбрать товар'),
#     'INFO': emojize(':speech_balloon: О магазине'),
#     'SETTINGS': emojize('⚙️ Настройки'),
#     'SHIRTS': emojize('👔 Рубашки'),
#     'T-SHIRTS': emojize('👕 Футболки'),
#     'PANTS': emojize('👖 Штаны'),
#     '<<': emojize('⏪'),
#     '>>': emojize('⏩'),
#     'BACK_STEP': emojize('◀️'),
#     'NEXT_STEP': emojize('▶️'),
#     'ORDER': emojize('✅ ЗАКАЗ'),
#     'X': emojize('❌'),
#     'DOWN': emojize('-'),
#     'AMOUNT_PRODUCT': COUNT,
#     'AMOUNT_ORDERS': COUNT,
#     'UP': emojize('+'),
#     'APPLY': '✅ Оформить заказ',
#     'COPY': '©️'
# }

# # id категорий продуктов
# CATEGORY = {
#     'SHIRTS': 1,
#     'T-SHIRTS': 2,
#     'PANTS': 3,
# }

# # названия команд
# COMMANDS = {
#     'START': "start",
#     'HELP': "help",
# }
