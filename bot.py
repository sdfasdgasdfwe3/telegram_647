import json
import os
import subprocess
import sys
import asyncio
from telethon import TelegramClient, events
from datetime import datetime, timedelta
import requests
import hashlib

# Список необходимых пакетов
required_packages = [
    'telethon',  # Библиотека для работы с Telegram API
    'requests'   # Для работы с запросами на GitHub
]

# Функция для проверки и установки недостающих пакетов
def check_install(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
        print(f"Пакет {package} успешно установлен.")
    else:
        print(f"Пакет {package} уже установлен.")

# Устанавливаем все необходимые пакеты
for package in required_packages:
    check_install(package)

# Путь к локальному файлу конфигурации на устройстве пользователя
CONFIG_FILE = '/data/data/com.termux/files/home/config.json'
BOT_FILE_PATH = '/data/data/com.termux/files/home/bot.py'

# Функция для проверки, прошло ли больше года с последнего обновления
def is_year_passed(last_update):
    now = datetime.now()
    return now - datetime.fromisoformat(last_update) > timedelta(days=365)

# Функция для проверки и скачивания последней версии файла с GitHub
def check_and_update_file():
    github_url = "https://raw.githubusercontent.com/sdfasdgasdfwe3/telegram_647/main/bot.py"
    response = requests.get(github_url)
    if response.status_code != 200:
        print(f"Ошибка при скачивании файла с GitHub: {response.status_code}")
        return

    with open(BOT_FILE_PATH, 'wb') as f:
        f.write(response.content)
    print("Файл bot.py обновлён до последней версии.")

# Проверка наличия и обновление конфигурационного файла
if os.path.exists(CONFIG_FILE):
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
        API_ID = config['api_id']
        API_HASH = config['api_hash']
        PHONE_NUMBER = config['phone_number']
        last_update = config['last_update']
        print(f"Данные загружены из конфигурации: API_ID={API_ID}, API_HASH={API_HASH}, PHONE_NUMBER={PHONE_NUMBER}")

        if is_year_passed(last_update):
            print("Прошел год с последнего обновления конфигурации. Пожалуйста, введите данные снова.")
            API_ID = int(input("Введите ваш API ID (число): "))
            API_HASH = input("Введите ваш API Hash: ").strip()
            PHONE_NUMBER = input("Введите ваш номер телефона: ").strip()

            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    'api_id': API_ID,
                    'api_hash': API_HASH,
                    'phone_number': PHONE_NUMBER,
                    'last_update': datetime.now().isoformat()
                }, f)
            print("Данные обновлены.")
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        print(f"Ошибка в файле конфигурации: {e}")
        sys.exit(1)

else:
    print("Файл конфигурации не найден, необходимо ввести данные вручную.")
    while True:
        try:
            API_ID = int(input("Введите ваш API ID (число): "))
            break
        except ValueError:
            print("API ID должно быть числом. Попробуйте снова.")
    API_HASH = input("Введите ваш API Hash: ").strip()
    while True:
        PHONE_NUMBER = input("Введите ваш номер телефона: ").strip()
        if PHONE_NUMBER.startswith('+') and len(PHONE_NUMBER) > 10:
            break
        else:
            print("Неверный формат номера телефона. Попробуйте снова.")
    with open(CONFIG_FILE, 'w') as f:
        json.dump({
            'api_id': API_ID, 
            'api_hash': API_HASH, 
            'phone_number': PHONE_NUMBER,
            'last_update': datetime.now().isoformat()
        }, f)
    print(f"Данные сохранены в конфигурации: API_ID={API_ID}, API_HASH={API_HASH}, PHONE_NUMBER={PHONE_NUMBER}")

# Инициализация клиента
client = TelegramClient('sessions', API_ID, API_HASH)

# Проверка и обновление файла bot.py с GitHub перед запуском
check_and_update_file()

# Добавим анимации текста
async def menu_animation(message):
    menu_text = """
    Список анимаций:
    1. Мерцание
    2. Бегущий текст
    3. Затмение
    4. Падение букв
    """
    await message.reply(menu_text)

# Функции для анимаций
def flicker(text, count=5):
    for _ in range(count):
        await client.send_message(message.chat.id, f"\u200b{text}")
        await asyncio.sleep(0.2)
        await client.send_message(message.chat.id, f"{text}")
        await asyncio.sleep(0.2)

def running_text(text):
    for i in range(len(text) + 1):
        await client.send_message(message.chat.id, text[:i])
        await asyncio.sleep(0.2)

def fade_text(message, text):
    for i in range(len(text)):
        await message.reply(text[:i])
        await asyncio.sleep(0.2)
    
def falling_letters(message, text):
    for letter in text:
        await message.reply(letter)
        await asyncio.sleep(0.3)

# Обработка команды "меню"
@client.on(events.NewMessage(pattern='/меню'))
async def handle_menu(event):
    await menu_animation(event)
    user_choice = await client.wait_for(events.NewMessage())
    if user_choice.text == '1':
        await flicker("Мерцание текста")
    elif user_choice.text == '2':
        await running_text("Бегущий текст")
    elif user_choice.text == '3':
        await fade_text(event, "Затмение текста")
    elif user_choice.text == '4':
        await falling_letters(event, "Падение букв")

if __name__ == "__main__":
    asyncio.run(main())
