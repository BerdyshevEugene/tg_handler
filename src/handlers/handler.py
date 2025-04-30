import abc
from mrkup.mrkup import Keyboard
from data_base.dbalchemy import DBManager


class Handler(metaclass=abc.ABCMeta):
    def __init__(self, bot):
        self.bot = bot
        self.keyboards = Keyboard()
        self.DB = DBManager()

    @abc.abstractmethod
    def handle(self):
        pass