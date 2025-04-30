from telegram import (
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    InlineKeyboardButton, InlineKeyboardMarkup
)
from settings import config
from .keyboard_constants import KEYBOARD


class Keyboard:
    '''
    класс для создания reply-клавиатур (кнопки внизу экрана)
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
        
        # создаем разметку с кнопками
        self.markup = ReplyKeyboardMarkup(
            keyboard=[  # добавляем список кнопок
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
        
        # создаем разметку с кнопкой
        self.markup = ReplyKeyboardMarkup(
            keyboard=[[itm_btn]],  # список кнопок
            resize_keyboard=True,
            input_field_placeholder='выберите действие'
        )
        return self.markup

    def remove_menu(self):
        return ReplyKeyboardRemove()
