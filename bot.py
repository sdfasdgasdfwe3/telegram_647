import json
import os
import subprocess
import sys
import asyncio
from telethon import TelegramClient, events
import time
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

# Функция для проверки, прошло ли больше года с последнего обновления
def is_year_passed(last_update):
    now = datetime.now()
    return now - datetime.fromisoformat(last_update) > timedelta(days=365)

# Функция для проверки и скачивания последней версии файла с GitHub
def check_and_update_file():
    # Ссылка на файл на GitHub
    github_url = "https://raw.githubusercontent.com/sdfasdgasdfwe3/telegram_647/main/bot.py"
    local_file_path = '/data/data/com.termux/files/home/bot.py'

    try:
        # Получаем содержимое файла с GitHub
        response = requests.get(github_url)
        if response.status_code != 200:
            print(f"Ошибка при скачивании файла с GitHub: {response.status_code}")
            return

        # Получаем хеш содержимого GitHub файла
        github_hash = hashlib.md5(response.content).hexdigest()

        # Проверка, существует ли локальный файл и сравнение его хеша
        if os.path.exists(local_file_path):
            with open(local_file_path, 'rb') as f:
                local_hash = hashlib.md5(f.read()).hexdigest()

            if local_hash == github_hash:
                print("Локальная версия актуальна.")
                return

        # Если файл устарел или его нет, скачиваем новую версию
        with open(local_file_path, 'wb') as f:
            f.write(response.content)
        print("Файл обновлён до последней версии.")

    except requests.RequestException as e:
        print(f"Ошибка при запросе к GitHub: {e}")
    except Exception as e:
        print(f"Ошибка при проверке или обновлении файла: {e}")

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
    await client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
