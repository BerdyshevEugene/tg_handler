# KoshkinBot (TG handler)
Бот помощник для ведения заметок и напоминаний. Можно работать как в самом боте, так и добавлять его в группу.
## Структура проекта:

```python
tg_handler
│
├── logger
│
├── src
│   ├── service
│   │   ├── db_connector.py - соединение с БД
│   │   ├── reminder.py - здесь функционал работы с напоминаниями: CRUD
│   │   ├── service_messages.py - рассылка служ. сообщений пользователям
│   │   └── weather.py - отправка погоды пользователям (в н.в. не использ.)
│   │
│   ├── handler.py - меню бота
│   ├── location_storage.py - определение местополож. польз.
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


## Остальная информация

FileDescription: KoshkinBot

InternalName: KoshkinBot

ProductName: KoshkinBot

Author: Berdyshev E.A.

Development and support: Berdyshev E.A.

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
