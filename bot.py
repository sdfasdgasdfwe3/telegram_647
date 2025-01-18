import json
import os
import subprocess
import sys
import asyncio
from telethon import TelegramClient, events
from datetime import datetime, timedelta
import requests  # Для работы с GitHub API
import hashlib  # Для проверки целостности файла

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
    # Ссылка на файл на GitHub
    github_url = "https://raw.githubusercontent.com/sdfasdgasdfwe3/telegram_647/main/bot.py"

    # Получаем хеш текущей версии файла на GitHub
    response = requests.get(github_url)
    if response.status_code != 200:
        print(f"Ошибка при скачивании файла с GitHub: {response.status_code}")
        return

    # Скачиваем файл на локальную машину
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
        
        # Проверка, прошло ли больше года с последнего запроса данных
        if is_year_passed(last_update):
            print("Прошел год с последнего обновления конфигурации. Пожалуйста, введите данные снова.")
            API_ID = int(input("Введите ваш API ID (число): "))
            API_HASH = input("Введите ваш API Hash: ").strip()
            PHONE_NUMBER = input("Введите ваш номер телефона: ").strip()

            # Обновляем файл конфигурации
            with open(CONFIG_FILE, 'w') as f:
                json.dump({
                    'api_id': API_ID,
                    'api_hash': API_HASH,
                    'phone_number': PHONE_NUMBER,
                    'last_update': datetime.now().isoformat()  # Обновляем дату последнего обновления
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

# Главная асинхронная функция
async def main():
    print("Запуск main()")
    await client.start(phone=PHONE_NUMBER)
    print("Скрипт успешно запущен! Отправьте команду '001' для выбора анимации.")

    # Команда для выбора анимации
    @client.on(events.NewMessage(pattern='/001'))
    async def handler(event):
        # Список анимаций
        animations = ['Анимация 1', 'Анимация 2', 'Анимация 3']
        await event.respond(f"Выберите анимацию: {', '.join(animations)}")
        
        # Ждём ответ от пользователя
        response = await client.wait_for(events.NewMessage(from_users=event.sender_id))
        selected_animation = response.text.strip()  # Обработать ответ от пользователя
        
        # Проверка на выбор анимации
        if selected_animation in animations:
            await event.respond(f"Вы выбрали: {selected_animation}")
            # Здесь можно обработать анимацию
            # После выбора анимации список скрывается
            await event.respond("Список анимаций скрыт. Вы выбрали анимацию.")
        else:
            await event.respond("Неверная анимация. Пожалуйста, выберите правильную анимацию.")

    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
