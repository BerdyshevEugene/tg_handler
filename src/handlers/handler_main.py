from handlers.handler_cmnd import HandlerCommands


class HandlerMain:
    '''класс-компоновщик для всех обработчиков'''
    def __init__(self, bot):
        self.bot = bot
        self.handler_commands = HandlerCommands(self.bot)

    def handle(self):
        '''запуск всех обработчиков'''
        self.handler_commands.handle()