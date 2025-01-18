import json
import os
import subprocess
import sys
import asyncio
from telethon import TelegramClient, events
import time
from datetime import datetime, timedelta

# Путь к локальному файлу конфигурации на устройстве пользователя
CONFIG_FILE = '/data/data/com.termux/files/home/config.json'  # Путь к файлу может быть другим на разных устройствах

# Функция для проверки и установки недостающих пакетов
def check_install(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"Пакет {package} успешно установлен.")
    else:
        print(f"Пакет {package} уже установлен.")

# Список необходимых пакетов
required_packages = [
    'telethon',  # Библиотека для работы с Telegram API
    'requests'   # Если используете запросы для обновлений или других целей
]

# Устанавливаем все необходимые пакеты
for package in required_packages:
    check_install(package)

# Функция для проверки, прошло ли больше года с последнего обновления
def is_year_passed(last_update):
    try:
        last_update_date = datetime.fromisoformat(last_update)
    except ValueError:
        return True  # Если формат даты некорректный, считаем, что обновление необходимо
    now = datetime.now()
    return now - last_update_date > timedelta(days=365)

# Функция для загрузки конфигурации из файла
def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Ошибка при чтении конфигурации: {e}")
    return None

# Функция для сохранения конфигурации в файл
def save_config(api_id, api_hash, phone_number):
    config = {
        'api_id': api_id,
        'api_hash': api_hash,
        'phone_number': phone_number,
        'last_update': datetime.now().isoformat()
    }
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)
    print("Конфигурация обновлена.")

# Проверяем, существует ли конфигурация
config = load_config()

# Если конфигурация существует, проверяем, нужно ли обновить данные
if config:
    API_ID = config.get('api_id')
    API_HASH = config.get('api_hash')
    PHONE_NUMBER = config.get('phone_number')
    last_update = config.get('last_update')
    
    print(f"Данные загружены из конфигурации: API_ID={API_ID}, API_HASH={API_HASH}, PHONE_NUMBER={PHONE_NUMBER}")
    
    # Если прошло больше года с последнего обновления, обновляем конфигурацию
    if is_year_passed(last_update):
        print("Прошел год с последнего обновления конфигурации. Пожалуйста, введите данные снова.")
        API_ID = int(input("Введите ваш API ID (число): "))
        API_HASH = input("Введите ваш API Hash: ").strip()
        PHONE_NUMBER = input("Введите ваш номер телефона: ").strip()
        
        # Сохраняем обновленные данные в конфигурации
        save_config(API_ID, API_HASH, PHONE_NUMBER)
else:
    print("Конфигурация не найдена или повреждена, необходимо ввести данные вручную.")
    API_ID = int(input("Введите ваш API ID (число): "))
    API_HASH = input("Введите ваш API Hash: ").strip()
    PHONE_NUMBER = input("Введите ваш номер телефона: ").strip()
    
    # Сохраняем введенные данные в конфигурации
    save_config(API_ID, API_HASH, PHONE_NUMBER)

# Инициализация клиента
client = TelegramClient('sessions', API_ID, API_HASH)

# Настройка скорости печатания (фиксированное значение)
typing_speed = 0.4

# Доступные анимации
animations = {
    1: "Засветка",
    2: "Секретный код",
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

animation_functions = {
    1: animate_brightness,
    2: animate_secret_code,
}

# Переменная для текущей анимации
current_animation = 1
awaiting_animation_choice = False
start_time = time.time()

# Обработчик команд
@client.on(events.NewMessage(outgoing=True))
async def handler(event):
    global current_animation, awaiting_animation_choice, start_time

    timeout = 30  # Таймаут в секундах
    if awaiting_animation_choice and time.time() - start_time > timeout:
        awaiting_animation_choice = False
        await event.respond("Время выбора анимации вышло. Повторите попытку.")

    if event.raw_text == "001":
        animations_list = "\n".join([f"{key}) {value}" for key, value in animations.items()])
        message = await event.respond(f"Доступные анимации:\n{animations_list}\nВыберите номер анимации:")
        await event.delete()  # Удаляем команду "001"
        awaiting_animation_choice = True
        start_time = time.time()
        return

    elif awaiting_animation_choice:
        if event.raw_text.isdigit():
            choice = int(event.raw_text)
            if choice in animations:
                current_animation = choice
                awaiting_animation_choice = False
                start_time = time.time()
                await event.delete()  # Удаляем список анимаций
                await event.respond(f"Вы выбрали анимацию: {animations[choice]}\n"
                                    "Чтобы анимировать текст, отправьте команду /р <ваш текст>")
            else:
                await event.respond("Неверный номер анимации. Попробуйте снова.")
        else:
            await event.respond("Пожалуйста, введите числовое значение для выбора анимации.")

    elif event.raw_text.startswith('/р '):
        text_to_animate = event.raw_text[3:].strip()
        if not text_to_animate:
            await event.edit("Ошибка: Текст для анимации не может быть пустым.")
            return
        if len(text_to_animate) > 200:
            await event.edit("Ошибка: текст слишком длинный. Используйте текст до 200 символов.")
            return
        try:
            await animation_functions[current_animation](event, text_to_animate)
        except Exception as e:
            print(f"Ошибка при выполнении анимации: {e}")
            await event.edit(f"Произошла ошибка при выполнении анимации: {e}")

# Главная асинхронная функция
async def main():
    print("Запуск main()")
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Отправьте команду '001' для выбора анимации.")
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
