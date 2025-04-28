# KoshkinBot (TG handler)
Бот помощник для ведения заметок и напоминаний. Можно работать как в самом боте, так и добавлять его в группу.
## Структура проекта:

```python
tg_handler
│
├── logger
│
├── src
│   ├── handlers - содержит все обработчики команд
│   │   ├── base_handler.py - содержит базовые обработчики: меню со всеми кнопками
│   │   ├── base_handler.py - здесь реализуется базовый функционал: старт, запуск меню с кнопками
│   │   ├── handler.py - здесь реализуется функционал: добавить, удалить, показать лист напоминаний
│   │   ├── month_handler.py - обработчик и отрисовка календаря с напоминаниями
│   │   └── service_message_handler.py - рассылка служебных сообщений пользователю
│   │
│   ├── logger
│   │
│   ├── service
│   │   ├── db_connector.py - соединение с БД
│   │   ├── location_storage.py - логика хранения и получения локации пользователя
│   │   ├── reminder.py - здесь функционал работы с напоминаниями: CRUD
│   │   ├── service_messages.py - рассылка служ. сообщений пользователям
│   │   └── weather.py - отправка погоды пользователям (в н.в. не использ.)
│   │
│   └── main.py - основной файл программы для запуска
│
├── requirements.txt - зависимости
└── README.md
```

## Инструкция
1. создайте и активируйте виртуальное окружение и установите зависимости:
```python
py -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. для отправки служебных сообщений в файле handler.py в переменную messagе, пропишите сообщение. Служебное сообщение отправляется из бота по команде /service


## История версий:
- 1.0.1: добавлена функция отображения текущего месяца/задач (тестовый режим);

## Остальная информация

FileDescription: KoshkinBot

InternalName: KoshkinBot

ProductName: KoshkinBot

Author: Berdyshev E.A.

Development and support: Berdyshev E.A.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
