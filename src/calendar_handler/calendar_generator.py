from calendar import monthrange, day_name
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont


def generate_calendar_image(year, month, tasks):
    width, height = 700, 500
    background_color = (255, 255, 255)
    line_color = (0, 0, 0)
    task_color = (255, 0, 0)

    # создание изображения
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)

    # настройка шрифта
    try:
        font = ImageFont.truetype('arial.ttf', 12)
    except IOError:
        font = ImageFont.load_default()

    # создание сетки дней
    days_in_month = monthrange(year, month)[1]
    # для 6 строк, включая имена дней
    day_width, day_height = width // 7, (height - 30) // 6
    # заголовок месяца
    draw.text((width // 2 - 40, 10),
              f'{month}-{year}', fill=line_color, font=font)
    # имена дней недели
    for i, day_name in enumerate(day_name[:7]):
        draw.text((i * day_width + 5, 30),
                  day_name[:2], fill=line_color, font=font)
    # заполнение дней
    current_day = 1
    for row in range(1, 6):  # 5 недель максимум
        for col in range(7):
            x, y = col * day_width, row * day_height + 50
            if row == 1 and col < datetime(year, month, 1).weekday():
                continue
            if current_day > days_in_month:
                break

            # отрисовка дня
            draw.rectangle([x, y, x + day_width, y +
                           day_height], outline=line_color)
            draw.text((x + 5, y + 5), str(current_day),
                      fill=line_color, font=font)

            # отметка задачи для текущего дня, если есть
            task_list = tasks.get(current_day, [])
            for i, task in enumerate(task_list):
                draw.text((x + 5, y + 20 + i * 15),
                          task[:10], fill=task_color, font=font)

            current_day += 1
    # cохранение изображения
    img_path = f'calendar_{year}_{month}.png'
    img.save(img_path)
    return img_path
