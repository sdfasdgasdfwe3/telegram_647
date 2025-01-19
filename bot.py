import json
import os
import asyncio
from datetime import datetime
from telethon import TelegramClient, events

# Файл для хранения данных
CONFIG_FILE = 'config.json'

# Проверяем, существует ли файл конфигурации
if os.path.exists(CONFIG_FILE):
    with open(CONFIG_FILE, 'r') as f:
        config = json.load(f)
    API_ID = config['api_id']
    API_HASH = config['api_hash']
    PHONE_NUMBER = config['phone_number']
else:
    API_ID = int(input("Введите ваш API ID: "))
    API_HASH = input("Введите ваш API Hash: ")
    PHONE_NUMBER = input("Введите ваш номер телефона (в формате +375XXXXXXXXX, +7XXXXXXXXXX): ")
    with open(CONFIG_FILE, 'w') as f:
        json.dump({'api_id': API_ID, 'api_hash': API_HASH, 'phone_number': PHONE_NUMBER}, f)

# Инициализация клиента
client = TelegramClient('sessions', API_ID, API_HASH)

# Настройка скорости печатания
while True:
    try:
        typing_speed = float(input("Введите скорость печатания (от 0.1 до 0.5): "))
        if 0.1 <= typing_speed <= 0.5:
            break
        else:
            print("Введите значение в диапазоне от 0.1 до 0.5.")
    except ValueError:
        print("Пожалуйста, введите числовое значение.")

# Доступные анимации
animations = {
    1: "Засветка",
    2: "Секретный код",
    3: "Линия загрузки",
}

# Реализация анимаций
async def animate_brightness(event, text):
    for i in range(len(text) + 1):
        await event.edit("░" * (len(text) - i) + text[:i])
        await asyncio.sleep(typing_speed)

async def animate_secret_code(event, text):
    import random
    for i in range(len(text) + 1):
        fake_text = ''.join(random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789') for _ in range(len(text)))
        await event.edit(fake_text[:i] + text[i:])
        await asyncio.sleep(typing_speed)
    await event.edit(text)

async def animate_loading_line(event, text):
    progress_bar = ["[          ]", "[=         ]", "[==        ]", "[===       ]", "[====      ]", "[=====     ]", "[======    ]", "[=======   ]", "[========  ]", "[========= ]", "[==========]"]
    for i in range(len(progress_bar)):
        await event.edit(f"{progress_bar[i]} {text}")
        await asyncio.sleep(typing_speed)

animation_functions = {
    1: animate_brightness,
    2: animate_secret_code,
    3: animate_loading_line,
}

# Переменная для текущей анимации
current_animation = 1
# Флаг для отображения выбора анимации
awaiting_animation_choice = False

# Обработчик команды "Меню"
@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    global current_animation, awaiting_animation_choice

    if event.raw_text.lower() == "меню":
        local_time = datetime.now().strftime("%H:%M:%S")
        menu_text = (
            f"<b>Меню настроек</b>\n"
            f"1) Текущая анимация: {animations[current_animation]}\n"
            f"2) Местное время: {local_time}\n"
            f"3) Смена анимации (отправьте номер анимации, например: 1)\n"
        )
        await event.respond(menu_text, parse_mode='html')

    elif awaiting_animation_choice:
        if event.raw_text.isdigit():
            choice = int(event.raw_text)
            if choice in animations:
                current_animation = choice
                awaiting_animation_choice = False
                await event.respond(f"Анимация изменена на: {animations[choice]}")
            else:
                await event.respond("Неверный номер анимации. Попробуйте снова.")
        else:
            await event.respond("Пожалуйста, введите числовое значение для выбора анимации.")

    elif event.raw_text == "3":
        awaiting_animation_choice = True
        animations_list = "\n".join([f"{key}) {value}" for key, value in animations.items()])
        await event.respond(f"Доступные анимации:\n{animations_list}\nВыберите номер анимации:")

    elif event.raw_text.startswith('/p '):
        text_to_animate = event.raw_text[3:]  # Текст для анимации после команды /p

        # Проверяем длину текста
        if len(text_to_animate) > 200:
            await event.edit("Ошибка: текст слишком длинный. Используйте текст до 200 символов.")
            return

        try:
            await animation_functions[current_animation](event, text_to_animate)
        except Exception as e:
            print(f"Ошибка при выполнении анимации: {e}")

async def main():
    print("Запуск main()")
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Отправьте команду 'Меню' для выбора анимации.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
