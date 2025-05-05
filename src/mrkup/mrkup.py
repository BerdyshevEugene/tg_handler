from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from settings import config
from .keyboard_constants import KEYBOARD


class Keyboard:
    '''
    класс для создания reply-клавиатур
    '''
    def __init__(self):
        self.markup = None

    def set_btn(self, name):
        return KeyboardButton(KEYBOARD[name])

    def start_menu(self):
        '''
        создает разметку кнопок в основном меню
        '''
        itm_btn_1 = self.set_btn('список напоминаний')
        itm_btn_2 = self.set_btn('добавить напоминание')
        itm_btn_3 = self.set_btn('удалить напоминание')
        itm_btn_4 = self.set_btn('показать календарь')
        itm_btn_5 = self.set_btn('инфо')

        self.markup = ReplyKeyboardMarkup(
            keyboard=[
                [itm_btn_1],
                [itm_btn_2, itm_btn_3],
                [itm_btn_4],
                [itm_btn_5]
            ],
            resize_keyboard=True, 
            one_time_keyboard=False,
            input_field_placeholder='выберите действие'
        )
        return self.markup

    def info_menu(self):
        itm_btn = self.set_btn('<<')

        self.markup = ReplyKeyboardMarkup(
            keyboard=[[itm_btn]],  # список кнопок
            resize_keyboard=True,
            input_field_placeholder='выберите действие'
        )
        return self.markup

    def reminder_type_menu(self):
        '''
        создает меню выбора типа напоминания (одноразовое/регулярное)
        '''
        itm_btn_1 = self.set_btn('одноразовое')
        itm_btn_2 = self.set_btn('регулярное')
        itm_btn_back = self.set_btn('<<')

        self.markup = ReplyKeyboardMarkup(
            keyboard=[
                [itm_btn_1, itm_btn_2],
                [itm_btn_back]
            ],
            resize_keyboard=True,
            input_field_placeholder='выберите тип напоминания'
        )
        return self.markup

    def frequency_menu(self):
        '''
        создает меню выбора периодичности для регулярных напоминаний
        '''
        itm_btn_1 = self.set_btn('ежедневно')
        itm_btn_2 = self.set_btn('еженедельно')
        itm_btn_3 = self.set_btn('ежемесячно')
        itm_btn_4 = self.set_btn('ежегодно')
        itm_btn_back = self.set_btn('<<')
        
        self.markup = ReplyKeyboardMarkup(
            keyboard=[
                [itm_btn_1, itm_btn_2],
                [itm_btn_3, itm_btn_4],
                [itm_btn_back]
            ],
            resize_keyboard=True,
            input_field_placeholder='выберите периодичность напоминаний'
        )
        return self.markup

    def remove_menu(self):
        return ReplyKeyboardRemove()
