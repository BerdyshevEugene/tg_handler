from PIL import Image, ImageDraw, ImageFont
import io
import calendar
import datetime

from telegram import Update
from telegram.ext import ContextTypes


def generate_calendar_image(month_name: str, year: int, month: int, reminders: dict) -> io.BytesIO:
    '''генерирует изображение календаря с напоминаниями'''
    config = {
        'cell_size': 80,
        'padding': 20,
        'header_height': 40,
        'font_size': 20,
        'small_font_size': 20,
        'highlight_color': 'red',
        'text_color': 'black',
        'bg_color': 'white'
    }

    # создаём изображение
    img_width = 7 * config['cell_size'] + 2 * config['padding']
    img_height = 8 * config['cell_size'] + 2 * \
        config['padding'] + config['header_height']
    img = Image.new('RGB', (img_width, img_height), config['bg_color'])
    draw = ImageDraw.Draw(img)

    # загрузка шрифтов
    try:
        font = ImageFont.truetype('arial.ttf', config['font_size'])
        small_font = ImageFont.truetype('arial.ttf', config['small_font_size'])
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # рисуем заголовок
    title = f'напоминания на {month_name}'
    title_width = draw.textlength(title, font=font)
    draw.text(
        ((img_width - title_width) // 2, config['padding']),
        title,
        font=font,
        fill=config['text_color']
    )

    # рисуем сетку календаря
    grid_top = config['padding'] + config['header_height']

    # дни недели
    days = ['Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб', 'Вс']
    for i, day in enumerate(days):
        x = config['padding'] + i * config['cell_size'] + \
            (config['cell_size'] - draw.textlength(day, font=font)) // 2
        y = grid_top + (config['cell_size'] - config['font_size']) // 2
        draw.text((x, y), day, font=font, fill=config['text_color'])

    # границы ячеек
    for i in range(8):
        y = grid_top + i * config['cell_size']
        draw.line(
            (config['padding'], y, config['padding'] +
             7 * config['cell_size'], y),
            fill=config['text_color'],
            width=1
        )
    for i in range(8):
        x = config['padding'] + i * config['cell_size']
        draw.line(
            (x, grid_top, x, grid_top + 7 * config['cell_size']),
            fill=config['text_color'],
            width=1
        )

    # заполнение календаря датами
    cal = calendar.Calendar(firstweekday=0)
    for week_idx, week in enumerate(cal.monthdayscalendar(year, month)):
        for day_idx, day in enumerate(week):
            if day == 0:
                continue

            x = config['padding'] + day_idx * \
                config['cell_size'] + config['cell_size'] // 2
            y = grid_top + (week_idx + 1) * \
                config['cell_size'] + config['cell_size'] // 2

            # выделение дней с напоминаниями
            if day in reminders:
                circle_radius = 15
                draw.ellipse([
                    x - circle_radius, y - circle_radius - 5,
                    x + circle_radius, y + circle_radius - 5
                ], fill=config['highlight_color'])
                text_color = 'white'
            else:
                text_color = config['text_color']

            # число месяца
            day_str = str(day)
            text_width = draw.textlength(day_str, font=font)
            draw.text(
                (x - text_width // 2, y - config['font_size'] // 2 - 5),
                day_str,
                font=font,
                fill=text_color
            )

    # добавляем список напоминаний
    reminders_text = '\n'.join([f'• {day} {datetime.date(year, month, 1).strftime("%B")}: {text}'
                                for day, text in reminders.items()])
    draw.text(
        (config['padding'], grid_top + 7 * config['cell_size'] + 10),
        reminders_text,
        font=small_font,
        fill=config['text_color']
    )

    # конвертируем в bytes
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    img_byte_arr.seek(0)
    return img_byte_arr


async def month_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''обработчик команды/кнопки для показа напоминаний'''
    query = update.callback_query
    # проверяет, был ли вызов функции через inline-кнопку или через команду
    user_id = query.from_user.id if query else update.effective_user.id

    now = datetime.datetime.now()
    month_name = now.strftime('%B %Y')
    reminders = {
        25: 'сходить к врачу',
        28: 'оплатить счёт'
    }

    image_bytes = generate_calendar_image(
        month_name=month_name,
        year=now.year,
        month=now.month,
        reminders=reminders
    )

    await context.bot.send_photo(
        chat_id=user_id,
        photo=image_bytes,
        caption=f'📅 ваши напоминания на {month_name}'
    )
