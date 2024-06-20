import re
import asyncio
from telethon import TelegramClient, events
from telethon.errors import PeerIdInvalidError
from telethon.tl.types import PeerChannel
from flask import Flask
from threading import Thread

# Укажите свои данные API
api_id = 22602269
api_hash = 'abec38892149524fd9da9a6f6ef9a90e'
phone_number = '+375298591476'  # Телефонный номер учетной записи пользователя
bot_token = '7206581932:AAG94yqHN0ipoCkkz2LpmD6SDGcc8_LDmkQ'  # Токен вашего бота

# Удалите существующий файл сессии (если есть)
import os

session_file = 'session_name.session'
if os.path.exists(session_file):
    os.remove(session_file)

# Создаем клиента для пользователя и для бота
client = TelegramClient('session_name', api_id, api_hash)
bot_client = TelegramClient('bot_session_name', api_id, api_hash).start(bot_token=bot_token)


@client.on(events.NewMessage(chats=-1001681248280))  # Замените на ID вашего канала
async def handle_user_message(event):
    message = event.message
    print(f"Received message as user: {message.text}")
    await process_message(message.text)


async def process_message(text):
    if 'Герой, отправляйся в Главу' in text or 'Отправляйся в' in text:
        # Поиск чисел после "Герой, отправляйся в Главу"
        pattern_hero = r'Герой, отправляйся в Главу (\d+)[^0-9]*(\d+)'
        match_hero = re.search(pattern_hero, text)

        # Поиск чисел после "Отправляйся в"
        pattern_go = r'Отправляйся в (\d+)[^0-9]*(\d+)'
        match_go = re.search(pattern_go, text)

        if match_hero:
            first_number = match_hero.group(1)
            second_number = match_hero.group(2)
            extracted_text = f"{first_number}-{second_number}"
            print(f"Extracted text from 'Герой, отправляйся в Главу': {extracted_text}")
            await send_message_as_bot(extracted_text)

        elif match_go:
            first_number = match_go.group(1)
            second_number = match_go.group(2)
            extracted_text = f"{first_number}-{second_number}"
            print(f"Extracted text from 'Отправляйся в': {extracted_text}")
            await send_message_as_bot(extracted_text)


async def send_message_as_bot(text):
    try:
        # Получаем объект InputPeer для канала (замените на свой ID канала)
        entity = await bot_client.get_entity(PeerChannel(-1002233650685))
        await bot_client.send_message(entity, text)
        print(f"Message sent as bot: {text}")
    except PeerIdInvalidError:
        print("Invalid Peer ID. Make sure the bot is added to the channel.")
    except Exception as e:
        print(f"Error sending message as bot: {e}")


async def start_client():
    try:
        print("Starting Telegram client...")
        await client.start(phone_number)
        print("Listening for new messages...")
        await client.run_until_disconnected()
    except ConnectionError as ce:
        print(f"Connection error occurred: {ce}")
    except asyncio.CancelledError:
        print("Task was cancelled")
    except Exception as e:
        print(f"Error starting Telegram client: {e}")


async def start_bot_client():
    try:
        print("Starting bot client...")
        await bot_client.start()
    except Exception as e:
        print(f"Error starting bot client: {e}")


def run_flask():
    app = Flask('')

    @app.route('/')
    def home():
        return "I'm alive"

    app.run(host='0.0.0.0', port=80)


def keep_alive():
    t = Thread(target=run_flask)
    t.start()


if __name__ == '__main__':
    keep_alive()  # Запускаем Flask приложение для поддержки активности сервера

    # Запускаем асинхронные задачи в одном цикле событий
    loop = asyncio.get_event_loop()
    asyncio.ensure_future(start_client())
    asyncio.ensure_future(start_bot_client())
    loop.run_forever()
