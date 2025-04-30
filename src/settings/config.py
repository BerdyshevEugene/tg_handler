import os

from dotenv import load_dotenv
from emoji import emojize

VERSION = '1.0.1'
AUTHOR = 'E.N.'
TOKEN = os.getenv('TG_BOT_TOKEN')
GROUP_ID = os.getenv('GROUP_ID')


# родительская директория
# BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# путь до базы данных
load_dotenv()
DATABASE = (
    f'postgresql+psycopg2://'
    f'{os.getenv("POSTGRES_USER")}:'
    f'{os.getenv("POSTGRES_PASSWORD")}@'
    f'localhost:5432/'
    f'{os.getenv("POSTGRES_DB")}'
)

# COUNT = 0

# кнопки управления
KEYBOARD = {
}

# # id категорий продуктов
# CATEGORY = {
# }

# # названия команд
# COMMANDS = {
#     'START': "start",
#     'HELP': "help",
# }
